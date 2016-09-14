import logging
import shutil
import os
from shutil import copyfile, move

logger = logging.getLogger()


class SummaryProcessor(object):
    SUMMARY_FILE = 'summary.txt'

    def __process_summary(self, directory):
        """
        Read the summary.txt file produced by Droidmate's exploration and extract the monitored API calls
        :param directory: Directory where the summary file is located
        :return: List of identified APIs
        """

        # Read summary file
        summary_file = os.path.join(directory, self.SUMMARY_FILE)
        f = open(summary_file, 'r')
        lines = f.readlines()
        f.close()

        # Extract information from summary file
        data = []
        l = len(lines)
        i = 0
        while i < l:
            # Api list
            if 'pairs count observed' in lines[i]:
                # Jump to list start
                i += 3
                while (i < l) and (not '==================' in lines[i]):
                    line = lines[i]

                    # Line don't have a resId so caption is in the description, sometimes the caption is long and
                    # break the default formatting of the file
                    offset = 98
                    if '[' in line:
                        start_idx = line.index('[')
                        end_idx = line.index(']')
                        caption_size = end_idx - start_idx

                        # 10 is a fixed offset between the caption and the data (after)
                        # 25 is a fixed offset between the start of the line and the caption
                        if caption_size + 25 > offset:
                            offset = caption_size + start_idx + 10

                    line = line[offset:]

                    # Replace the URI parameter for the content URI. This is necessary because ContentResolver.query
                    # method can be used to access different methods including: sms, call logs, and external storage.
                    # Example:
                    # android.content.ContentResolver: void registerContentObserver(android.net.Uri,boolean,android.database.ContentObserver)
                    # content://settings/secure/accessibility_captioning_edge_color
                    # if there is an URI parameter (ContentResolver class) get the parameter value
                    tmp = line.split('uri: ')

                    # if there is a parameter, replace
                    parameter = 'android.net.Uri'
                    if len(tmp) > 1:
                        parameter = "'%s'" % tmp[-1].strip()

                    # Get the API call
                    res = tmp[0].split(':')
                    # Replace the URI parameter with its value
                    res = [x.replace('android.net.Uri', parameter).strip() for x in res]
                    # Remvoe the return type from the method's name
                    if len(res) == 2:
                        res[1] = res[1].split(' ')[1]
                    data += [res]
                    i += 1

            i += 1

        data = [d for d in data if len(d) > 1]

        return data

    @staticmethod
    def __write_api_list(api_list, result_directory):
        """
        Write a file containing the API list for the application
        :param api_list: List of identified APIs, idx0 = class name, idx1 = method signature
        :param result_directory: Directory to save the API list
        """

        path = os.path.join(result_directory, 'api_list.txt')
        logger.debug('Writting API list file %s', path)
        f = open(path, 'w')

        f.write('%s\t%s\n' % ('class_name', 'method_signature'))
        for class_name, method_signature, in api_list:
            f.write('%s\t%s\n' % (class_name, method_signature))

        f.close()

    def process(self, apks, results_directory):
        """
        Check in the results directory for all APKs that were explored and extract the list of APIs from each of the
        applications
        :param apks: List of APKs to be verified
        :param results_directory: Base directory where the exploration results were stores
        :return: List of APIs per application
        """
        assert results_directory is not None
        assert os.path.exists(results_directory)

        processed_summaries = []

        for apk in apks:
            logger.debug('Processing results for APK %s', apk)
            path = os.path.join(results_directory, apk.get_apk_name_as_directory_name())
            if os.path.exists(path):
                data = self.__process_summary(path)
                self.__write_api_list(data, path)
                processed_summary = [apk, data]
                processed_summaries.append(processed_summary)
            else:
                logger.warn('No results found for APK %s', apk)

        return processed_summaries