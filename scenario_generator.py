import logging
import os

logger = logging.getLogger()
mapping = {
    "android.app.ActivityManager->getRunningTasks(int)":
        [#'Name="system" Id="%d" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="system" Method="Srv_getTasks" Restricted="%s" Asked="false" />'],
    "android.app.ActivityManager->getRecentTasks(int,int)":
        [#'Name="system" Id="%d" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="system" Method="Srv_getRecentTasks" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://call_log/calls',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="calling" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="calling" Method="CallLogProvider" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/contacts',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/contacts" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/contacts/1/photo',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/contacts" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/data',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/data" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/data/postals',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/data" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/data/phones',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/data" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/profile',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/profile" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://com.android.contacts/profile/photo',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="contacts" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="contacts" Method="contacts/profile" Restricted="%s" Asked="false" />'],
    "android.content.ContentResolver->query('content://sms',java.lang.String[],java.lang.String,java.lang.String[],java.lang.String,android.os.CancellationSignal)":
        [#'<Restriction Id="%d" Name="messages" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="messages" Method="SmsProvider" Restricted="%s" Asked="false" />'],
    "android.hardware.Camera->open(int)":
        [#'<Restriction Id="%d" Name="media" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="media" Method="Camera.permission" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getBestProvider(android.location.Criteria,boolean)":
        [#'<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getBestProvider" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getLastKnownLocation(java.lang.String)":
        [#'<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getLastLocation" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->getProviders(boolean)":
        [#'<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_getProviders" Restricted="%s" Asked="false" />'],
    "android.location.LocationManager->isProviderEnabled(java.lang.String)":
        [#'<Restriction Id="%d" Name="location" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="location" Method="Srv_isProviderEnabled" Restricted="%s" Asked="false" />'],
    "android.telephony.TelephonyManager->getDeviceId()":
        [#'<Restriction Id="%d" Name="phone" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="phone" Method="Srv_getDeviceId5" Restricted="%s" Asked="false" />'],
    "java.net.Socket->connect(java.net.SocketAddress,int)":
        [#'<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="internet" Method="inet" Restricted="%s" Asked="false" />'],
    "java.net.URL->openConnection()":
        [#'<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
         '<Restriction Id="%d" Name="internet" Method="inet" Restricted="%s" Asked="false" />'],
    "org.apache.http.impl.client.AbstractHttpClient->execute(org.apache.http.HttpHost,org.apache.http.HttpRequest,org.apache.http.protocol.HttpContext)":
        [#'<Restriction Id="%d" Name="internet" Restricted="%s" Asked="false" />',
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
        """if 'content://' in api:
            # Identify opening ' and ignore it
            idx = api.index("'") + 1
            api_call_as_file_name = api[:api.index("'", idx)]
        else:
            api_call_as_file_name = api[:api.index('(')]"""

        tmp = api.split('->')
        class_name = tmp[0]
        method_name = tmp[1]

        # Get only the class name
        class_name = class_name.split('.')[-1]

        if 'content://' in method_name:
            tmp = method_name.split("'")
            method_name = tmp[0] + '__' + method_name[1]
        else:
            method_name = method_name.split("(")[0]

        api_call_as_file_name = class_name + "_" + method_name
        api_call_as_file_name = api_call_as_file_name.replace("://", '___') \
            .replace("://", '____') \
            .replace("/", '_____')
        """api_call_as_file_name = api_call_as_file_name.replace('->', '_') \
            .replace("('", '__') \
            .replace("://", '___') \
            .replace("://", '____') \
            .replace("/", '_____')"""

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

    @staticmethod
    def __read_configuration_file(config_path):
        """
        Read the configuration file and mark all apis as "do not ask"
        :param config_path: Configuration file path
        :return: Configuration data
        """
        f = file(config_path)
        config = f.readlines()
        f.close()

        # Remove any permission that may be marked as "ask"
        #config = [w.replace('Asked="true"', 'Asked="false"') for w in config]

        return config

    @staticmethod
    def __apply_configuration_template(config, apk):
        """
        Read the configuration file template
        :param config: APK specific configuration data
        :param apk: APK
        :return: Configuration data template
        """
        f = file('mockable_apis_template.xml')
        template_config = f.readlines()
        f.close()

        apk_id = ScenarioGenerator.__get_package_id(config, apk)
        package_name = apk.get_package()

        # Remove any permission that may be marked as "ask"
        new_config = [w.replace('**ID**', str(apk_id)).replace('**PACKAGE**', package_name) for w in template_config]

        return new_config


    '''@staticmethod
    def __clean_configuration(config, package_id):
        """
        Remove all other application from the configuration
        :param config: Configuration data
        :param package_id: Id of the package that should remain in the configuration file
        :return: Clean configuration data
        """
        # Remove other applications from configuration file
        tmp = [w for w in config
               if (('"%d"' % package_id) in w)
               or ("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>" in w)
               or ("<XPrivacy>" in w)
               or ("</XPrivacy>" in w)
               ]

        tmp = [w for w in tmp if not '"OnDemand"' in w and not '"true"' in w]

        new_data = ['  <Setting Id="%d" Type="" Name="Blacklist" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="Freeze" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="IntentWall" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="ModifyTime" Value="1473796514705" /> ',
                    '  <Setting Id="%d" Type="" Name="NoResolve" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="NoUsageData" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="Notify" Value="false" /> ', #true
                    '  <Setting Id="%d" Type="" Name="OnDemand" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="OnDemandSystem" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="PermMan" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="Resolve" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="SafeMode" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="State" Value="0" /> ',
                    '  <Setting Id="%d" Type="" Name="TestVersions" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="Updates" Value="false" /> ',
                    '  <Setting Id="%d" Type="" Name="WhitelistNoModify" Value="false" />  '
                    ]

        for l in reversed(new_data):
            tmp.insert(3, l % package_id + '\n')

        return tmp'''

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

                base_config = ScenarioGenerator.__read_configuration_file(base_config_path)
                base_config = ScenarioGenerator.__apply_configuration_template(base_config, apk)

                package_id = self.__get_package_id(base_config, apk)
                apk_directory = os.path.join(self.output_directory, apk.get_apk_name_as_directory_name())

                #base_config = ScenarioGenerator.__clean_configuration(base_config, package_id)

                if not os.path.exists(apk_directory):
                    os.mkdir(apk_directory)

                assert os.path.exists(apk_directory)

                # Sort APIs
                sorted_api_list, sorted_api_count = ScenarioGenerator.__sort_api_list(api_list, api_count)

                for api, count in zip(sorted_api_list, sorted_api_count):
                    logger.debug('API found %s (%d)', api, count)
                    # Check is is mapped
                    if api in mapping.keys():
                        logger.info('API is mockable, generating scenario (%s)', api)
                        pending_changes = mapping[api]
                        output_filename = self.__get_filename(apk_directory, api)
                        logger.info('Scenario filename: %s', output_filename)
                        save_file = True

                        new_config = base_config[:]
                        # Perform changes
                        for change in pending_changes:
                            #false_value = change % (package_id, 'false')
                            false_value = change % (package_id, '**RESTRICTED**')
                            true_value = change % (package_id, 'true')

                            # Change specific configuration
                            tmp_config = new_config[:]
                            new_config = [w.replace(false_value, true_value) for w in new_config]

                            #assert new_config != tmp_config
                            if new_config == tmp_config:
                                logger.error('Unable to restrict API %s, item not found in configuration file (%s)' % (true_value, apk))
                                save_file = False

                        if save_file:
                            # Remove all remaining **RESTRICTED**
                            new_config = [w.replace('**RESTRICTED**', 'false') for w in new_config]

                            # Write output file
                            f = open(output_filename, 'w')
                            f.writelines(new_config)
                            f.close()

                    else:
                        logger.debug('API is not mockable (%s)', api)
            else:
                logger.error('Base XPrivacy configuration file not found for %s', apk)