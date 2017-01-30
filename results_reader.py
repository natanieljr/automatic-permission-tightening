from logging.config import fileConfig
import logging
import os
import threading
from math import sqrt
from auxiliar import read_file
from scenario_generator import mapping as mp


class ExplorationResult(object):
    threshold = None,
    scenario = None,
    size = None,
    app = None,
    scenario = None
    initial_expl_observed = 0
    initial_expl_explored = 0
    scenario_observed = 0
    scenario_explored = 0
    result005 = None
    result010 = None
    result015 = None
    result020 = None
    result030 = None
    result040 = None
    result050 = None
    API_calls_total = 0
    API_calls_blocked = 0
    uniq_API_calls_total = 0
    uniq_API_calls_blocked = 0
    APIs = []
    exception = ''

    def uniq_API_calls_perc(self):
        if self.uniq_API_calls_total != 0:
            return self.uniq_API_calls_blocked / float(self.uniq_API_calls_total)
        else:
            return 0.0

    def API_calls_perc(self):
        if self.API_calls_total != 0:
            return self.API_calls_blocked / float(self.API_calls_total)
        else:
            return 0.0

    def qtd_APIs(self):
        return len(self.APIs)

    def get_dists(self):
        dist1 = sqrt(pow(self.initial_expl_observed, 2) + pow(self.initial_expl_explored, 2))
        dist2 = sqrt(pow(self.scenario_observed, 2) + pow(self.scenario_explored, 2))

        return [dist1, dist2, abs(dist1 - dist2)]


def get_result(obs1, expl1, obs2, expl2, threshold):
    # d(E_0, E_x) = \sqrt{(expl(E_0) - expl(E_x)) ^ 2 + (obs(E_0) - obs(E_x)) ^ 2}
    dist1 = sqrt(pow(expl1, 2) + pow(obs1, 2))
    dist2 = sqrt(pow(expl2, 2) + pow(obs2, 2))

    # Comparing to ROOT
    # return abs(dist1 - dist2) < (dist1 * 0.05)
    # return abs(dist1 - dist2) < (dist1 * 0.10)
    # return abs(dist1 - dist2) < (dist1 * 0.15)
    # return abs(dist1 - dist2) < (dist1 * 0.20)
    # return abs(dist1 - dist2) < (dist1 * 0.30)
    # return abs(dist1 - dist2) < (dist1 * 0.40)
    return abs(dist1 - dist2) < (dist1 * threshold)


def get_exception_data(scenario_file):
    exception_file = os.path.join(scenario_file, 'logs', 'exceptions.txt').replace('/scenarios/', '/exploration/')

    if os.path.exists(exception_file):
        exception_data = read_file(exception_file)
        return exception_data[3].split(':')[-2].strip() + ': ' + exception_data[3].split(':')[-1].strip()

    return ''


logger = logging.getLogger()

mapping = [
    ["Srv_getRecentTasks", "android.app.ActivityManager->getRecentTasks(int,int)"],
    ["Srv_getTasks", "android.app.ActivityManager->getRunningTasks(int)"],
    ["CallLogProvider", "android.content.ContentResolver->query('content://call_log/calls',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/contacts", "android.content.ContentResolver->query('content://com.android.contacts/contacts',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/contacts", "android.content.ContentResolver->query('content://com.android.contacts/contacts/1/photo',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/data", "android.content.ContentResolver->query('content://com.android.contacts/data',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/data", "android.content.ContentResolver->query('content://com.android.contacts/data/phones',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/data", "android.content.ContentResolver->query('content://com.android.contacts/data/postals',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/profile", "android.content.ContentResolver->query('content://com.android.contacts/profile',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["contacts/profile", "android.content.ContentResolver->query('content://com.android.contacts/profile/photo',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["SmsProvider", "android.content.ContentResolver->query('content://sms',java.lang.String[],,java.lang.String,java.lang.String[],,java.lang.String,android.os.CancellationSignal)"],
    ["Camera.permission", "android.hardware.Camera->open(int)"],
    ["Srv_getBestProvider", "android.location.LocationManager->getBestProvider(android.location.Criteria,boolean)"],
    ["Srv_getLastLocation", "android.location.LocationManager->getLastKnownLocation(java.lang.String)"],
    ["Srv_getProviders", "android.location.LocationManager->getProviders(boolean)"],
    ["Srv_isProviderEnabled", "android.location.LocationManager->isProviderEnabled(java.lang.String)"],
    ["Srv_getDeviceId5", "android.telephony.TelephonyManager->getDeviceId()"],
    ["inet", "java.net.Socket->connect(java.net.SocketAddress,int)"],
    ["inet", "java.net.URL->openConnection()"],
    ["inet", "org.apache.http.impl.client.AbstractHttpClient->execute(org.apache.http.HttpHost,org.apache.http.HttpRequest,org.apache.http.protocol.HttpContext)"]
]
sensitive_apis_mapping = mp.keys()

fileConfig('logging_config.ini')
result = []
#d = 'data/app_did_not_crash/scenarios/'
base_dir = 'data/obs_expl/'

for threshold in reversed(os.listdir(base_dir)):
    threshold_dir = os.path.join(base_dir, threshold, 'scenarios')
    for apis_blocked in os.listdir(threshold_dir):
        # Debug
        #if apis_blocked != '2-api-blocked':
        #    continue

        logger.info('Processing results in directory %s' % apis_blocked)
        apis_blocked_dir = os.path.join(os.path.join(threshold_dir, apis_blocked))
        for application in os.listdir(apis_blocked_dir):
            # Debug
            #if g != 'com.ng.dailynews_v1_13':
            #    continue

            logger.info('Processing results in directory %s' % application)
            expl_dir = os.path.join(os.path.join(apis_blocked_dir, application))

            if (not os.path.isdir(expl_dir)) or ('unchanged' in expl_dir):
                continue

            for scenario in os.listdir(expl_dir):
                logger.info('Processing results in directory %s' % scenario)
                scenario_file = os.path.join(os.path.join(expl_dir, scenario))
                scenario_data = read_file(scenario_file)

                expl_res = ExplorationResult()
                expl_res.app = application
                expl_res.scenario = scenario
                expl_res.size = int(apis_blocked[0])
                expl_res.threshold = float(threshold)
                expl_res.exception = get_exception_data(scenario_file)
                expl_res.APIs = []

                stats_file = os.path.join('data/exploration/first-run', application, 'aggregate_stats.txt')
                if os.path.exists(stats_file):
                    stats_data = read_file(stats_file)[1].split('\t')
                    expl_res.initial_expl_observed = int(stats_data[5].strip())
                    expl_res.initial_expl_explored = int(stats_data[6].strip())

                if expl_res.size == 1:
                    stats_file_scenario = os.path.join('data/exploration/1-api-blocked', application, scenario, 'aggregate_stats.txt')
                else:
                    stats_file_scenario = os.path.join(scenario_file.replace('\\scenarios\\', '/exploration/'), 'aggregate_stats.txt')
                if os.path.exists(stats_file_scenario):
                    stats_data_scenario = read_file(stats_file_scenario)
                    if len(stats_data_scenario) > 1:
                        stats_data_scenario = stats_data_scenario[1].split('\t')
                        expl_res.scenario_observed = int(stats_data_scenario[5].strip())
                        expl_res.scenario_explored = int(stats_data_scenario[6].strip())

                expl_res.result005 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.05)
                expl_res.result010 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.10)
                expl_res.result015 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.15)
                expl_res.result020 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.20)
                expl_res.result030 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.30)
                expl_res.result040 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.40)
                expl_res.result050 = get_result(expl_res.initial_expl_observed, expl_res.initial_expl_explored,
                                                expl_res.scenario_observed, expl_res.scenario_explored, 0.50)

                for item in mapping:
                    restriction = item[0]
                    api = item[1].replace(',,', ',')
                    #api = 'java.net.Socket->connect(java.net.SocketAddress,int)'

                    api_list_path = os.path.join('data/exploration/first-run', application, 'summarized_api_list.txt')
                    #first_run_path = 'C:/Users/natan_000/Desktop/Saarland/repositories/automatic-permission-tightening/data/exploration/first-run/animaonline.android.wikiexplorer_v1_5_5/summarized_api_list.txt'

                    if not os.path.exists(api_list_path):
                        logger.error('Missing initial exploration %s' % application)
                        break

                    # Remove header
                    api_list = read_file(api_list_path)[1:]

                    # Reset counter, only last one is valid
                    expl_res.API_calls_total = 0
                    expl_res.uniq_API_calls_total = 0

                    for api_list_item in api_list:
                        line_data = api_list_item.split('\t')
                        if len(line_data) == 2:
                            tmp_api = line_data[0]
                            tmp_qtd = int(line_data[1].strip())

                            # Count only sensitive APIs
                            if tmp_api in sensitive_apis_mapping:
                                expl_res.API_calls_total += tmp_qtd
                                expl_res.uniq_API_calls_total += 1

                                if tmp_api == api:
                                    # Count API blocked in scenario
                                    for line in scenario_data:
                                        if ('true' in line) and (restriction in line):
                                            #logger.info('Mapped %s -> %s' % (restriction, api))

                                            expl_res.API_calls_blocked += tmp_qtd
                                            expl_res.uniq_API_calls_blocked += 1
                                            expl_res.APIs.append(api)
                                            break

                found = filter(lambda x: (x.app == expl_res.app) and (x.qtd_APIs() == expl_res.qtd_APIs()) and len([api for api in x.APIs if api not in expl_res.APIs]) == 0, result)
                if found == []:
                    result.append(expl_res)
                else:
                    logger.debug('Scenario already included, ignoring.')
                    pass

# Sleep to prevent problems printing the data
threading._sleep(1)

for r in result:
    tmp = ''
    for a in r.APIs:
        tmp += '\t%s' % a

    i = r.qtd_APIs()
    while i <= 8:
        tmp += '\t-'
        i += 1

    print('%.2f' % r.threshold + '\t' +
          str(r.size) + '\t' +
          str(r.app) + '\t' +
          str(r.scenario) + '\t' +
          str(r.initial_expl_observed) + '\t' +
          str(r.initial_expl_explored) + '\t' +
          str(r.scenario_observed) + '\t' +
          str(r.scenario_explored) + '\t' +
          '%.2f' % r.get_dists()[0] + '\t' +
          '%.2f' % r.get_dists()[1] + '\t' +
          '%.2f' % r.get_dists()[2] + '\t' +
          '%.2f' % (r.get_dists()[2]/max(r.get_dists()[0], 1)) + '\t' +
          '%d' % r.result005 + '\t' +
          '%d' % r.result010 + '\t' +
          '%d' % r.result015 + '\t' +
          '%d' % r.result020 + '\t' +
          '%d' % r.result030 + '\t' +
          '%d' % r.result040 + '\t' +
          '%d' % r.result050 + '\t' +
          str(r.API_calls_total) + '\t' +
          str(r.API_calls_blocked) + '\t' +
          str(r.API_calls_perc()) + '\t' +
          str(r.uniq_API_calls_total) + '\t' +
          str(r.uniq_API_calls_blocked) + '\t' +
          str(r.uniq_API_calls_perc()) + '\t' +
          str(r.qtd_APIs()) + '\t' +
          tmp.strip()
          )