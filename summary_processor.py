import logging
import operator
import os

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
        Write a file containing the list of APIs for the application
        :param api_list: List of identified APIs, idx0 = class name, idx1 = method signature
        :param result_directory: Directory to save the API list
        """

        path = os.path.join(result_directory, 'api_list.txt')
        logger.debug('Writting API list file %s', path)
        f = open(path, 'w')

        f.write('%s\t%s\n' % ('class_name', 'method_signature'))
        for class_name, method_signature in api_list:
            f.write('%s\t%s\n' % (class_name, method_signature))

        f.close()

    @staticmethod
    def __write_summarized_api_list(api_list, api_count, result_directory):
        """
        Write a file containing the list of APIs invoked by the application and the number of times it was called
        :param api_list: List of identified APIs, idx0 = class name, idx1 = method signature
        :param result_directory: Directory to save the API list
        """

        path = os.path.join(result_directory, 'summarized_api_list.txt')
        logger.debug('Writting summarized API list file %s', path)
        f = open(path, 'w')

        f.write('%s\t%s\n' % ('method_signature', 'count'))
        for method_signature, count in zip(api_list, api_count):
            f.write('%s\t%d\n' % (method_signature, count))

        f.close()

    def extract_apis(self, apks, results_directory):
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

    def count_api_calls_per_apk(self, processed_summaries, results_directory):
        """
        Count the number of times each API was called in each apk
        :param processed_summaries: List of API calls per APK
        :return: Summarized list of API calls per APK
        """
        result = []

        for apk, log in processed_summaries:
            logger.debug('Counting APIs for %s', apk)

            api_list = []
            api_count = []

            for class_name, method_signature in log:
                key = '%s->%s' % (class_name, method_signature)
                if key not in api_list:
                    api_list.append(key)
                    api_count.append(1)
                else:
                    idx = api_list.index(key)
                    api_count[idx] += 1

            path = os.path.join(results_directory, apk.get_apk_name_as_directory_name())
            self.__write_summarized_api_list(api_list, api_count, path)

            result.append([apk, api_list, api_count])

        return result

    def count_api_calls(self, summarized_apis, results_directory):
        """
        Count the number of times each API was called in each apk
        :param processed_summaries: List of API calls per APK
        :return: Summarized list of API calls per APK
        """
        api_list = []
        api_count = []

        logger.debug('Counting APIs')
        for apk, apk_api_list, apk_api_count in summarized_apis:

            for key, count in zip(apk_api_list, apk_api_count):
                if key not in api_list:
                    api_list.append(key)
                    api_count.append(count)
                else:
                    idx = api_list.index(key)
                    api_count[idx] += count

        self.__write_summarized_api_list(api_list, api_count, results_directory)
        return [api_list, api_count]
