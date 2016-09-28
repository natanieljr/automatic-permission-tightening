from logging.config import fileConfig
import logging
import argparse
import os
import shutil

from consts import *
from libs.apk_adapter import APKAdapter
from configuration_extractor import XPrivacyConfigurationExtractor
from apk_inliner import ApkInliner
from droidmate_executor import DroidmateExecutor
from summary_processor import SummaryProcessor
from scenario_generator import ScenarioGenerator

logger = logging.getLogger()


class Main(object):
    """"
    Main application class, for mor information run the script with -h parameter
    """

    args = None
    apks = []

    def __init__(self, arguments, configurator_extractor=XPrivacyConfigurationExtractor()):
        """
        Create a new instance of the application
        :param arguments: Command line arguments
        """
        logger.info("Initializing application")
        logger.debug("Work directory: %s", os.getcwd())
        self.args = arguments
        self.configurator_extractor = configurator_extractor
        self.__validate()
        self.__initialize()

    def get_inlined_apk_dir(self):
        """
        Return the directory where inlined APKs should be stored. This directory is a subdirectory of the temporary
        directory
        :return: Inlined APKs directory
        """
        return os.path.join(self.args.tmpDir, "inlined")

    def get_original_apk_dir(self):
        if args.apk is not None:
            return os.path.dirname(args.apk)

        return args.directory

    @staticmethod
    def __recreate_directory(directory):
        """
        Check if the directory exists, if the directory exists than delete it and recreate
        """
        assert directory is not None

        if os.path.exists(directory):
            logger.warn("Directory '%s' already exists, it will be deleter and recreated", directory)
            shutil.rmtree(directory)

        os.mkdir(directory)
        assert os.path.exists(directory)
        assert os.path.isdir(directory)

    def __populate_apk_list(self, file_list):
        """
        Create APK objects for each file, extract package name and version
        :param file_list: List of APK files to be processed
        """
        for f in file_list:
            apk = APKAdapter(f)
            logger.debug('APK created: %s (%s)', f, apk)
            self.apks.append(apk)

    def __validate(self):
        if not self.args.keepDirectories:
            logger.debug("Configuring output directory: %s", self.args.output)
            self.__recreate_directory(self.args.output)
            logger.debug("Configuring temporary directory: %s", self.args.tmpDir)
            self.__recreate_directory(self.args.tmpDir)
        else:
            logger.debug("Keeping output directory: %s", self.args.output)
            logger.debug("Keeping temporary directory: %s", self.args.tmpDir)

    def __initialize(self):
        """
        Initialize the APK list
        :return:
        """
        file_list = []
        if self.args.apk is not None:
            logger.debug('Script configured for single APK processing: %s', self.args.apk)
            file_list.append(self.args.apk)
        else:
            logger.debug('Script configured for batch processing, directory: %s', self.args.directory)
            for f in os.listdir(self.args.directory):
                if f.lower().endswith(".apk"):
                    file_list.append(os.path.join(args.directory, f))

        # Create the APK list
        self.__populate_apk_list(file_list)

    def process(self):
        logger.info("Processing APK(s)")

        # Define the output directory for the extracted configuration files. Use application's temporary directory
        config_extraction_dir = os.path.join(args.tmpDir, 'extracted-config')

        if self.args.extractConfig:
            self.configurator_extractor.output_directory = config_extraction_dir
            self.configurator_extractor.process(self.apks)
        else:
            logger.info("Skipping 'Configuration extraction'")

        inlined_apk_dir = self.get_inlined_apk_dir()

        # Inline APKs
        if self.args.inline:
            apk_inliner = ApkInliner()
            apk_inliner.output_directory = inlined_apk_dir
            apk_inliner.set_tmp_directory(os.path.join(self.args.tmpDir, "apk-inliner"))
            apk_mapping = apk_inliner.process(self.apks)
        else:
            logger.info("Skipping 'Inline APKs'")

        executor_tmp_dir = os.path.join(self.args.tmpDir, 'processing')
        executor_output_dir = os.path.join(self.args.tmpDir, 'exploration')

        if not os.path.exists(executor_output_dir):
            os.mkdir(executor_output_dir)

        assert os.path.exists(executor_output_dir)

        executor_output_dir = os.path.join(executor_output_dir, 'first-run')

        # Run initial exploration
        if self.args.explore:
            assert self.args.inline
            droidmate_executor = DroidmateExecutor(inlined_apk_dir, executor_output_dir, executor_tmp_dir)
            droidmate_executor.first_exploration(self.apks, apk_mapping)
        else:
            logger.info("Skipping 'Explore'")

        # Extract APIs
        if self.args.extractAPIs:
            summary_processor = SummaryProcessor()
            processed_summaries = summary_processor.extract_apis(self.apks, executor_output_dir)

            # Print debug messages
            for apk, log in processed_summaries:
                logger.debug('Listing APIs for %s', apk)
                for class_name, method_signature in log:
                    logger.debug('--%s->%s', class_name, method_signature)

            summarized_api_list_apk = summary_processor.count_api_calls_per_apk(processed_summaries, executor_output_dir)

            # Print debug messages
            for apk, api_list, api_count in summarized_api_list_apk:
                logger.debug('Summarized API list for %s', apk)
                for method_signature, count in zip(api_list, api_count):
                    logger.debug('--%s\t%d', method_signature, count)

            summarized_api_list = summary_processor.count_api_calls(summarized_api_list_apk, executor_output_dir)

            # Print debug messages
            logger.debug('Summarized API list')
            summarized_api_name, summarized_api_count = summarized_api_list
            for method_signature, count in zip(summarized_api_name, summarized_api_count):
                logger.debug('--%s\t%d', method_signature, count)
        else:
            logger.debug("Skipping 'Extract APIs'")

        if self.args.generateScenarios:
            if self.args.extractAPIs:
                scenario_output_dir = os.path.join(self.args.tmpDir, 'scenarios')

                if not os.path.exists(scenario_output_dir):
                    os.mkdir(scenario_output_dir)

                assert os.path.exists(scenario_output_dir)

                scenario_output_dir = os.path.join(scenario_output_dir, '1-api-blocked')
                scenario_generator = ScenarioGenerator(config_extraction_dir, scenario_output_dir)
                scenario_generator.generate_scenarios(summarized_api_list_apk)
            else:
                logger.error('It is not possible to generate scenarios without extracting APIs')

        for apk in self.apks:
            logger.debug("Processing APK %s", apk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    # Input
    group.add_argument(ARG_APK_SHORT, ARG_APK, type=str, metavar='Path',
                       help='APK file to be processed (process single file)')
    group.add_argument(ARG_DIR_SHORT, ARG_DIR, type=str, metavar='Directory',
                       help='Directory containing APKs to be processed (batch processing)')

    # Output and tmp directories
    parser.add_argument(ARG_OUT_SHORT, ARG_OUT, type=str, metavar='Directory', default='output',
                        help="Output directory")
    parser.add_argument(ARG_TMP_SHORT, ARG_TMP, type=str, metavar='Directory', default='tmp',
                        help='Temporary directory')

    # Keep directories
    parser.add_argument(ARG_KEEP_DIR, dest='keepDirectories', action='store_true',
                        help="Do not remove output and tmp directories "
                             "(the internal directories may still be removed during processing)")
    parser.add_argument(ARG_KEEP_DIR_NO, dest='keepDirectories', action='store_false',
                        help="Do not remove output and tmp directories "
                             "(the internal directories may still be removed during processing)")
    parser.set_defaults(keepDirectories=False)

    # Extract configuration
    parser.add_argument(ARG_CFG, dest='extractConfig', action='store_true',
                        help="Execute 'Extract XPrivacy's configuration files' process")
    parser.add_argument(ARG_CFG_NO, dest='extractConfig', action='store_false',
                        help="Do not execute 'Extract XPrivacy's configuration files' process")
    parser.set_defaults(extractConfig=True)

    # Inline
    parser.add_argument(ARG_INLINE, dest='inline', action='store_true',
                        help="Execute 'Inline APKs' process")
    parser.add_argument(ARG_INLINE_NO, dest='inline', action='store_false',
                        help="Do not execute 'Inline APKs' process")
    parser.set_defaults(inline=True)

    # Run initial exploration
    parser.add_argument(ARG_EXPLORE, dest='explore', action='store_true',
                        help="Execute 'Run initial exploration' process")
    parser.add_argument(ARG_EXPLORE_NO, dest='explore', action='store_false',
                        help="Do not execute 'Run initial exploration' process")
    parser.set_defaults(explore=True)

    # Extract APIs from summary
    parser.add_argument(ARG_EXTRACT_APIS, dest='extractAPIs', action='store_true',
                        help="Execute 'Extract API list' process")
    parser.add_argument(ARG_EXTRACT_APIS_NO, dest='extractAPIs', action='store_false',
                        help="Do not execute 'Extract API list' process")
    parser.set_defaults(extractAPIs=True)

    # Generate scenarios
    parser.add_argument(ARG_GENERATE_SCENARIOS, dest='generateScenarios', action='store_true',
                        help="Generate XPrivacy's configuration files for different scenarios")
    parser.add_argument(ARG_GENERATE_SCENARIOS_NO, dest='generateScenarios', action='store_false',
                        help="Do not generate XPrivacy's configuration files for different scenarios")
    parser.set_defaults(generateScenarios=True)

    # Run scenarios
    parser.add_argument(ARG_GENERATE_SCENARIOS, dest='runScenarios', action='store_true',
                        help="Generate XPrivacy's configuration files for different scenarios")
    parser.add_argument(ARG_GENERATE_SCENARIOS_NO, dest='runScenarios', action='store_false',
                        help="Do not generate XPrivacy's configuration files for different scenarios")
    parser.set_defaults(runScenarios=True)


    args = parser.parse_args()

    fileConfig('logging_config.ini')

    main = Main(args)
    main.process()
