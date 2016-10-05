import logging
import os

logger = logging.getLogger()
mapping = {
    "android.app.ActivityManager->getRunningTasks(int)":
        ['Name="system" Id="%d" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="system" Method="Srv_getTasks" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://call_log/calls',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="calling" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="calling" Method="CallLogProvider" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/contacts',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/contacts" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/data',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/data" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/data/postals',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/data" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/profile',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/profile" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/profile/photo',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/profile" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://sms',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        ['<Restriction Id="%d" Name="messages" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="messages" Method="SmsProvider" Restricted="%s" Asked="false" />'],
    "android.hardware.Camera->open(int)":
        ['<Restriction Id="%d" Name="media" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="media" Method="Camera.permission" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getBestProvider(android.location.Criteria,boolean)":
        ['<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getBestProvider" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getLastKnownLocation(java.lang.String)":
        ['<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getLastLocation" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getProviders(boolean)":
        ['<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getProviders" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->isProviderEnabled(java.lang.String)":
        ['<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_isProviderEnabled" Restricted="%s" Asked="false" />'],
    "android.telephony.TelephonyManager->getDeviceId()":
        ['<Restriction Id="%d" Name="phone" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="phone" Method="Srv_getDeviceId5" Restricted="%s" Asked="false" />'],
    "java.net.Socket->connect(java.net.SocketAddress,int)":
        ['<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="internet" Method="inet" Restricted="%s" Asked="false" />'],
    "java.net.URL->openConnection()":
        ['<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="internet" Method="inet" Restricted="%s" Asked="false" />'],
    "org.apache.http.impl.client.AbstractHttpClient->execute(org.apache.http.HttpHost,org.apache.http.HttpRequest,org.apache.http.protocol.HttpContext)":
        ['<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="internet" Method="inet" Restricted="%s" Asked="false" />']
    }


class ScenarioGenerator(object):
    """
    Class that generate execution scenarios based on the identified API list
    """

    config_directory = None
    output_directory = None

    def __init__(self, config_directory, output_directory):
        """
        Initialize object
        :param config_directory: Directory where XPrivacy's configuration files are stored
        :param output_directory: Directory where the newly generated scenarios will be stored
        """
        self.config_directory = config_directory
        self.output_directory = output_directory

    def __get_filename(self, apk_directory, api):
        """
        Create a file name to a scenario based on the API that is being restricted
        :param apk_directory: Directory where the application specific scenarios should be stored
        :param api: API that is being restricted in this scenario
        :return: The filename for the scenario configuration file
        """

        # Define scenario filename
        if 'content://' in api:
            # Identify opening ' and ignore it
            idx = api.index("'") + 1
            api_call_as_file_name = api[:api.index("'", idx)]
        else:
            api_call_as_file_name = api[:api.index('(')]

        api_call_as_file_name = api_call_as_file_name.replace('->', '_') \
            .replace("('", '__') \
            .replace("://", '___') \
            .replace("://", '____') \
            .replace("/", '_____')

        filename = os.path.join(apk_directory, api_call_as_file_name) + '.xml'

        return filename

    @staticmethod
    def __sort_api_list(api_list, api_count):
        """
        Sort API listr based on the number of times it was invoked
        :param api_list: List of APIs
        :param api_count: Number of times each API was invoked
        :return: Sorted API_LIST, API_COUNT list
        """

        # Sort APIs
        sorted_api_list = []
        sorted_api_count = []
        for (x, y) in sorted(zip(api_list, api_count), key=lambda pair: pair[1], reverse=True):
            sorted_api_list.append(x)
            sorted_api_count.append(y)

        return sorted_api_list, sorted_api_count

    @staticmethod
    def __get_package_id(config, apk):
        """
        Identify the package ID on XPrivacy's configuration file. This ID is used to index all permissions.
        :param config:
        :param apk:
        :return:
        """
        package = apk.get_package()

        id = -1
        for line in config:
            if ('PackageInfo' in line) and (package in line):
                start = line.index('"') + 1
                end = line.index('"', start)
                id = int(line[start:end])

        assert id >= 0

        return id

    def generate_scenarios(self, summarized_api_list_apk):
        """
        Generate scenarios with a single API being restricted. Each scenario will be saved in a configuration file
        :param summarized_api_list_apk: List of API calls per APK
        :return: void
        """
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

        assert os.path.exists(self.output_directory)

        for apk, api_list, api_count in summarized_api_list_apk:
            logger.info('Generating scenarios for %s', apk)

            base_config_path = os.path.join(self.config_directory, apk.get_apk_name_as_directory_name()) + '.xml'
            if os.path.exists(base_config_path):
                f = file(base_config_path)
                base_config = f.readlines()
                f.close()

                package_id = self.__get_package_id(base_config, apk)
                apk_directory = os.path.join(self.output_directory, apk.get_apk_name_as_directory_name())

                if not os.path.exists(apk_directory):
                    os.mkdir(apk_directory)

                assert os.path.exists(apk_directory)

                # Sort APIs
                sorted_api_list, sorted_api_count = ScenarioGenerator.__sort_api_list(api_list, api_count)


                for api, count in zip(sorted_api_list, sorted_api_count):
                    logger.debug('Relevant API found %s (%d)', api, count)
                    # Check is is mapped
                    if api in mapping.keys():
                        pending_changes = mapping[api]
                        output_filename = self.__get_filename(apk_directory, api)

                        new_config = base_config[:]
                        # Perform changes
                        for change in pending_changes:
                            false_value = change % (package_id, 'false')
                            true_value = change % (package_id, 'true')

                            new_config = [new_config.replace(false_value, true_value) for w in new_config]

                        # Write output file
                        f = open(output_filename, 'w')
                        f.writelines(new_config)
                        f.close()

                    else:
                        #logger.debug("Unmapped API %s", api)
                        pass
            else:
                logger.error('Base XPrivacy configuration file not found for %s', apk)