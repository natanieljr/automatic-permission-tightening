from logging.config import fileConfig
import logging
import argparse
import os
import shutil

from consts import *
from libs.apk_adapter import APKAdapter
from configuration_extractor import XPrivacyConfigurationExtractor
from apk_inliner import ApkInliner

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
        logger.debug("Configuring output directory: %s", self.args.output)
        self.__recreate_directory(self.args.output)
        logger.debug("Configuring temporary directory: %s", self.args.tmpDir)
        self.__recreate_directory(self.args.tmpDir)

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
        #self.configurator_extractor.output_directory = os.path.join(args.tmpDir, EXTRACTED_CFG_FOLDER)
        #self.configurator_extractor.process(self.apks)

        # Inline APKs
        apk_inliner = ApkInliner()
        apk_inliner.output_directory = self.get_inlined_apk_dir()
        apk_inliner.set_tmp_directory(os.path.join(self.args.tmpDir, "apk_inliner"))
        apk_inliner.process(self.apks)

        for apk in self.apks:
            logger.debug("Processing APK %s", apk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(ARG_APK_SHORT, ARG_APK, type=str, metavar='Path',
                       help='APK file to be processed (process single file)')
    group.add_argument(ARG_DIR_SHORT, ARG_DIR, type=str, metavar='Directory',
                       help='Directory containing APKs to be processed (batch processing)')
    parser.add_argument(ARG_CFG_SHORT, ARG_CFG, type=bool, metavar='Boolean', default=True,
                        help="Only extract XPrivacy's configuration file for the APK")
    parser.add_argument(ARG_OUT_SHORT, ARG_OUT, type=str, metavar='Directory', default='output',
                        help="Output directory")
    parser.add_argument(ARG_TMP_SHORT, ARG_TMP, type=str, metavar='Directory', default='tmp',
                        help='Temporary directory')
    args = parser.parse_args()

    fileConfig('logging_config.ini')

    main = Main(args)
    main.process()
