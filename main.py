from logging.config import fileConfig
from shutil import copyfile
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
from output_comparison import OutputComparison
from auxiliar import *

logger = logging.getLogger()


class Main(object):
    """"
    Main application class, for mor information run the script with -h parameter
    """
    dir_extracted_cfg = None
    dir_inlined_apk = None
    dir_exploration_base = None
    dir_exploration_tmp = None
    dir_exploration_first = None
    dir_scenario_base = None

    memory = None
    args = None
    apks = []

    def __init__(self, arguments):
        """
        Create a new instance of the application
        :param arguments: Command line arguments
        """
        logger.info("Initializing application")
        logger.debug("Work directory: %s", os.getcwd())
        self.args = arguments
        self.__validate()
        self.__initialize()

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

        mkdir(directory)

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
            self.__extract_config(config_extraction_dir)
        else:
            logger.info("Skipping 'Configuration extraction'")

        inlined_apk_dir = self.get_inlined_apk_dir()

        # Inline APKs
        if self.args.inline:
            apk_mapping = self.__inline_apks(inlined_apk_dir)
        else:
            logger.info("Skipping 'Inline APKs'")

        executor_tmp_dir = os.path.join(self.args.tmpDir, 'processing')
        executor_output_dir = os.path.join(self.args.tmpDir, 'exploration')

        mkdir(executor_output_dir)
        first_run_output_dir = os.path.join(executor_output_dir, 'first-run')

        # Run initial exploration
        if self.args.explore:
            self.__def_first_exploration(inlined_apk_dir, first_run_output_dir, executor_tmp_dir, apk_mapping)
        else:
            logger.info("Skipping 'Explore'")

        # Extract APIs
        if self.args.extractAPIs:
            summarized_api_list_apk, summarized_api_list = self.__extract_apis(first_run_output_dir)
        else:
            logger.debug("Skipping 'Extract APIs'")

        scenario_output_dir = os.path.join(self.args.tmpDir, 'scenarios')
        mkdir(scenario_output_dir)
        api_blocked_1_scenario_output_dir = os.path.join(scenario_output_dir, '1-api-blocked')

        if self.args.generateScenarios:
            assert self.args.extractAPIs
            scenario_generator = ScenarioGenerator(config_extraction_dir, api_blocked_1_scenario_output_dir)
            scenario_generator.generate_scenarios_1_api_blocked(summarized_api_list_apk)

        api_blocked_1_output_dir = os.path.join(executor_output_dir, '1-api-blocked')
        mkdir(api_blocked_1_output_dir)

        for apk in self.apks:
            # Run scenarios
            if self.args.runScenarios:
                assert self.args.inline
                #assert self.args.generateScenarios
                if apk_mapping.has_key(apk.get_basename()):
                    droidmate_executor = DroidmateExecutor(inlined_apk_dir, api_blocked_1_output_dir, executor_tmp_dir)
                    droidmate_executor.error_directory = os.path.join(api_blocked_1_output_dir, 'fail')

                    # Locate the scenario files
                    scenario_list = os.path.join(api_blocked_1_scenario_output_dir, apk.get_apk_name_as_directory_name())
                    if os.path.exists(scenario_list) and os.path.isdir(scenario_list):
                        for scenario in os.listdir(scenario_list):
                            tmp = os.path.join(scenario_list, scenario)
                            droidmate_executor.run_scenario(apk, apk_mapping, tmp)
            else:
                logger.info("Skipping 'Run Scenarios'")

        if args.appCrashed:
            # Use 'Application did not crash comparison'
            output_comparer = OutputComparison(first_run_output_dir)
            comparison_results = output_comparer.compare_with_apk_did_not_crash(api_blocked_1_output_dir, self.apks)

        """
        if args.runScenariosComposite:
            assert args.appCrashed

            api_blocked_2_scenario_output_dir = os.path.join(scenario_output_dir, '2-api-blocked')
            mkdir(api_blocked_2_scenario_output_dir)

            scenario_generator = ScenarioGenerator(config_extraction_dir, api_blocked_2_scenario_output_dir)
            unchanged_scenarios = scenario_generator.generate_scenarios_combined_api_blocked(api_blocked_1_scenario_output_dir, comparison_results)
            #for apk, scenario1, scenario2, new_scenario in unchanged_scenarios:

            api_blocked_2_output_dir = os.path.join(executor_output_dir, '2-api-blocked')
            mkdir(api_blocked_2_output_dir)

            for apk in self.apks:
                assert self.args.inline
                # assert self.args.generateScenarios
                if apk_mapping.has_key(apk.get_basename()):
                    droidmate_executor = DroidmateExecutor(inlined_apk_dir, api_blocked_2_output_dir,
                                                           executor_tmp_dir)
                    droidmate_executor.error_directory = os.path.join(api_blocked_2_output_dir, 'fail')

                    # Locate the scenario files
                    scenario_list = os.path.join(api_blocked_2_scenario_output_dir,
                                                 apk.get_apk_name_as_directory_name())
                    if os.path.exists(scenario_list) and os.path.isdir(scenario_list):
                        for scenario in os.listdir(scenario_list):
                            tmp = os.path.join(scenario_list, scenario)
                            droidmate_executor.run_scenario(apk, apk_mapping, tmp)
        """
        api_blocked_2_scenario_output_dir = os.path.join(scenario_output_dir, '2-api-blocked')
        mkdir(api_blocked_2_scenario_output_dir)

        scenario_generator = ScenarioGenerator(config_extraction_dir, api_blocked_2_scenario_output_dir)
        unchanged_scenarios = scenario_generator.generate_scenarios_combined_api_blocked(api_blocked_1_scenario_output_dir,
                                                                                         comparison_results)

    #############
    #############
    #############
    #############
    #############
    #############
    def _set_directories(self):
        # Define the output directory for the extracted configuration files. Use application's temporary directory
        self.dir_extracted_cfg = os.path.join(args.tmpDir, 'extracted-config')
        self.dir_inlined_apk = os.path.join(self.args.tmpDir, "inlined")
        self.dir_exploration_base = os.path.join(self.args.tmpDir, 'exploration')
        self.dir_exploration_tmp = os.path.join(self.args.tmpDir, 'processing')
        self.dir_exploration_first = os.path.join(self.dir_exploration_base, 'first-run')
        self.dir_exploration_1api = os.path.join(self.dir_exploration_base, '1-api-blocked')
        self.dir_scenario_base = os.path.join(self.args.tmpDir, 'scenarios')
        self.dir_scenario_1api = os.path.join(self.dir_scenario_base, '1-api-blocked')

        mkdir(self.dir_extracted_cfg)
        mkdir(self.dir_inlined_apk)
        mkdir(self.dir_exploration_base)
        mkdir(self.dir_exploration_tmp)
        mkdir(self.dir_exploration_first)
        mkdir(self.dir_scenario_base)
        mkdir(self.dir_scenario_1api)
        mkdir(self.dir_exploration_1api)

    def __extract_config(self):
        if self.args.extractConfig:
            cfg_extractor = XPrivacyConfigurationExtractor()
            cfg_extractor.output_directory = self.dir_extracted_cfg
            cfg_extractor.process(self.apks)
        else:
            logger.info("Skipping 'Configuration extraction'")

    def __inline_apks(self):
        apk_inliner = ApkInliner()
        apk_inliner.output_directory = self.dir_inlined_apk
        if self.args.inline:
            apk_inliner.set_tmp_directory(os.path.join(self.args.tmpDir, "apk-inliner"))
            apk_mapping = apk_inliner.process(self.apks)
        else:
            logger.info("Skipping 'Inline APKs'")

        # If the output directory exists, create the mapping
        if os.path.exists(self.dir_inlined_apk):
            logger.info("Creating mapping from output directory")
            # Map original APKs and inlined APKs
            apk_mapping = apk_inliner.create_apk_mapping(self.apks)

            return apk_mapping

        return {}

    def __first_exploration(self, inlined_apks):
        # Run initial exploration
        if self.args.explore:
            executor = DroidmateExecutor(self.dir_inlined_apk, self.dir_exploration_first, self.dir_exploration_tmp)
            executor.first_exploration(self.apks, inlined_apks)
        else:
            logger.info("Skipping 'Initial exploration'")

    def __extract_apis(self, exploration_dir):
        if self.args.extractAPIs:
            processor = SummaryProcessor()
            raw_api_list = processor.extract_apis(self.apks, exploration_dir)
            api_list_apk = processor.count_api_calls_per_apk(raw_api_list, exploration_dir)
            api_list = processor.count_api_calls(api_list_apk, exploration_dir)

            # Print RAW api calls
            for apk, log in raw_api_list:
                logger.debug('Listing APIs for %s', apk)
                for class_name, method in log:
                    logger.debug('--%s->%s', class_name, method)

            # Print debug messages
            for apk, methods, count in api_list_apk:
                logger.debug('Summarized API list for %s', apk)
                for method, value in zip(methods, count):
                    logger.debug('--%s\t%d', method, value)

            # Print debug messages
            logger.debug('Summarized API list')
            methods, values = api_list
            for method, value in zip(methods, values):
                logger.debug('--%s\t%d', method, value)
        else:
            logger.debug("Skipping 'Extract APIs'")
            api_list_apk = []
            api_list = []

        return  api_list_apk, api_list

    def __generate_scenarios_1api(self, api_list_apk):
        scenario_mapping = []
        if self.args.generateScenarios:
            scenario_generator = ScenarioGenerator(self.dir_extracted_cfg, self.dir_scenario_1api)
            scenario_mapping = scenario_generator.generate_scenarios_1_api_blocked(api_list_apk)
        else:
            logger.debug("Skipping 'Generate scenarios (1 API)'")

            file_name = os.path.join(self.dir_scenario_1api, 'mapping.txt')
            # If the output directory exists, create the mapping
            if os.path.exists(file_name):
                logger.info("Creating scenario mapping from file")
                f = open(file_name)
                data = f.readlines()
                f.close()

                for line in data:
                    tmp = line.strip().split('\t')
                    scenario_mapping.append(tmp)

        return scenario_mapping

    def __run_scenarios(self, inlined_apks):
        for apk in self.apks:
            key = apk.get_basename()
            if inlined_apks.has_key(key):
                executor = DroidmateExecutor(self.dir_inlined_apk, self.dir_exploration_1api, self.dir_exploration_tmp)

                # Locate the scenario files
                dir_apk = apk.get_apk_name_as_directory_name()
                scenario_list = os.path.join(self.dir_scenario_1api, dir_apk)
                if os.path.exists(scenario_list) and os.path.isdir(scenario_list):
                    # For each scenario, execute
                    for scenario in os.listdir(scenario_list):
                        scenario_path = os.path.join(scenario_list, scenario)
                        executor.run_scenario(apk, inlined_apks, scenario_path)

    def __compare_executions(self, exploration):
        evaluator = OutputComparison(self.dir_exploration_first)

        results = []
        if args.appCrashed:
            # Use 'Application did not crash comparison'
            results = evaluator.compare_with_apk_did_not_crash(exploration, self.apks)
        else:
            file_name = os.path.join(exploration, 'app_crashed_comp_results.txt')

            if os.path.exists(file_name):
                logger.info('Reading evaluation results from file')
                f = open(file_name)
                data = f.readlines()
                f.close()

                results = []
                for line in data:
                    tmp = line.strip().split('\t')
                    tmp[2] = bool(tmp[2])
                    tmp[3] = bool(tmp[3])
                    tmp[4] = bool(tmp[4])

                    results.append(tmp)

        return results

    def __combine_scenarios_and_run(self, initial_comparison, inlined_apks):
        if args.runScenariosComposite:
            old_scenario_dir = self.dir_scenario_1api
            nr_apis = 2

            equivalents = [w for w in initial_comparison if w[4]]
            while len(equivalents) > 0:
                scenario_dir = os.path.join(self.dir_scenario_base, '%d-api-blocked' % nr_apis)
                mkdir(scenario_dir)

                generator = ScenarioGenerator(self.dir_extracted_cfg, scenario_dir)
                unchanged = generator.generate_scenarios_combined_api_blocked(old_scenario_dir, equivalents, self.memory)
                #extra_mem_data = Main.__read_scenarios(scenario_dir)
                #self.memory += extra_mem_data

                # for apk, scenario1, scenario2, new_scenario in unchanged_scenarios:

                exploration_dir = os.path.join(self.dir_exploration_base, '%d-api-blocked' % nr_apis)
                mkdir(exploration_dir)

                for apk in self.apks:
                    if inlined_apks.has_key(apk.get_basename()):
                        executor = DroidmateExecutor(self.dir_inlined_apk, exploration_dir, self.dir_exploration_tmp)
                        executor.error_directory = os.path.join(exploration_dir, 'fail')

                        # Locate the scenario files
                        apk_dir = apk.get_apk_name_as_directory_name()
                        scenario_list = os.path.join(scenario_dir, apk_dir)
                        if os.path.exists(scenario_list) and os.path.isdir(scenario_list):
                            for scenario in os.listdir(scenario_list):
                                scenario_file = os.path.join(scenario_list, scenario)
                                #if nr_apis > 2:
                                executor.run_scenario(apk, inlined_apks, scenario_file)

                ###########
                comparison = self.__compare_executions(exploration_dir)
                equivalents = [w for w in comparison if w[4]]

                old_scenario_dir = scenario_dir
                nr_apis *= 2

    @staticmethod
    def __read_scenarios(scenario_dir):
        data = []

        if os.path.exists(scenario_dir) and os.path.isdir(scenario_dir):
            for apk in os.listdir(scenario_dir):
                apk_dir = os.path.join(scenario_dir, apk)
                if os.path.isdir(apk_dir):
                    for scenario in os.listdir(apk_dir):
                        scenario_file = os.path.join(apk_dir, scenario)
                        if os.path.isfile(scenario_file):
                            f = open(scenario_file)
                            tmp = f.readlines()
                            f.close()

                            data.append(tmp)

        return data

    def new_process(self):
        logger.info("(NEW) Processing APK(s)")

        # Configure directy's variables
        self._set_directories()

        # Extract configuration (if necessary)
        self.__extract_config()

        # Inline APKs (if necessary)
        inlined_apks = self.__inline_apks()

        # Execute first exploration (if necessary)
        self.__first_exploration(inlined_apks)

        # Extract APIs (if necessary)
        api_list_apk, api_list = self.__extract_apis(self.dir_exploration_first)

        # Generate individual scenarios (if necessary)
        #scenario_mapping = self.__generate_scenarios_1api(api_list_apk)
        self.__generate_scenarios_1api(api_list_apk)

        self.memory = Main.__read_scenarios(self.dir_scenario_1api)

        # Run scenarios
        if self.args.runScenarios:
            self.__run_scenarios(inlined_apks)
        else:
            logger.info("Skipping 'Run Scenarios'")

        comparison = self.__compare_executions(self.dir_exploration_1api)

        self.__combine_scenarios_and_run(comparison, inlined_apks)


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
    parser.set_defaults(extractConfig=False)

    # Inline
    parser.add_argument(ARG_INLINE, dest='inline', action='store_true',
                        help="Execute 'Inline APKs' process")
    parser.add_argument(ARG_INLINE_NO, dest='inline', action='store_false',
                        help="Do not execute 'Inline APKs' process")
    parser.set_defaults(inline=False)

    # Run initial exploration
    parser.add_argument(ARG_EXPLORE, dest='explore', action='store_true',
                        help="Execute 'Run initial exploration' process")
    parser.add_argument(ARG_EXPLORE_NO, dest='explore', action='store_false',
                        help="Do not execute 'Run initial exploration' process")
    parser.set_defaults(explore=False)

    # Extract APIs from summary
    parser.add_argument(ARG_EXTRACT_APIS, dest='extractAPIs', action='store_true',
                        help="Execute 'Extract API list' process")
    parser.add_argument(ARG_EXTRACT_APIS_NO, dest='extractAPIs', action='store_false',
                        help="Do not execute 'Extract API list' process")
    parser.set_defaults(extractAPIs=False)

    # Generate scenarios
    parser.add_argument(ARG_GENERATE_SCENARIOS, dest='generateScenarios', action='store_true',
                        help="Generate XPrivacy's configuration files for different scenarios")
    parser.add_argument(ARG_GENERATE_SCENARIOS_NO, dest='generateScenarios', action='store_false',
                        help="Do not generate XPrivacy's configuration files for different scenarios")
    parser.set_defaults(generateScenarios=False)

    # Run scenarios
    parser.add_argument(ARG_RUN_SCENARIOS, dest='runScenarios', action='store_true',
                        help="Generate XPrivacy's configuration files for different scenarios")
    parser.add_argument(ARG_RUN_SCENARIOS_NO, dest='runScenarios', action='store_false',
                        help="Do not generate XPrivacy's configuration files for different scenarios")
    parser.set_defaults(runScenarios=False)

    # Compare using 'App did not crash' metric
    parser.add_argument(ARG_APP_CRASH, dest='appCrashed', action='store_true',
                        help="Compare results using 'Application did not crash' metric")
    parser.add_argument(ARG_APP_CRASH_NO, dest='appCrashed', action='store_false',
                        help="Do not compare results using 'Application did not crash' metric")
    parser.set_defaults(appCrashed=False)

    # Run composite scenarios
    parser.add_argument(ARG_RUN_SCENARIOS_COMP, dest='runScenariosComposite', action='store_true',
                        help="Generate XPrivacy's configuration files for different, composite, scenarios and execute them")
    parser.add_argument(ARG_RUN_SCENARIOS_COMP_NO, dest='runScenariosComposite', action='store_false',
                        help="Do not generate XPrivacy's configuration files for different, composite, scenarios and execute them")
    parser.set_defaults(runScenariosComposite=False)

    args = parser.parse_args()

    fileConfig('logging_config.ini')

    main = Main(args)
    main.new_process()
