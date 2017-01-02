from logging.config import fileConfig
import logging
import os
from auxiliar import read_file
from scenario_generator import mapping as mp

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
d = 'data/obs_expl/0.50/scenarios/'
for f in os.listdir(d):
    logger.info('Processing results in directory %s' % f)
    fn = os.path.join(os.path.join(d, f))
    for g in os.listdir(fn):
        logger.info('Processing results in directory %s' % g)
        expl_dir = os.path.join(os.path.join(fn, g))

        if (not os.path.isdir(expl_dir)) or ('unchanged' in expl_dir):
            continue

        for h in os.listdir(expl_dir):
            logger.info('Processing results in directory %s' % h)
            scenario_file = os.path.join(os.path.join(expl_dir, h))
            scenario_data = read_file(scenario_file)

            for i in mapping:
                restriction = i[0]
                aa = i[1]
                api = aa.replace(',,', ',')
                #api = 'java.net.Socket->connect(java.net.SocketAddress,int)'

                fr_dir = 'data/exploration/first-run/%s' % g
                fr_path = os.path.join(fr_dir, 'summarized_api_list.txt')
                #fr_path = 'C:/Users/natan_000/Desktop/Saarland/repositories/automatic-permission-tightening/data/exploration/first-run/animaonline.android.wikiexplorer_v1_5_5/summarized_api_list.txt'

                if not os.path.exists(fr_path):
                    logger.error('Missing initial exploration %s' % g)
                    break

                fr_data = read_file(fr_path)
                # Remove header
                fr_data = fr_data[1:]

                nr_api_calls = 0
                nr_this_api_calls = 0
                total_api_calls = 0
                this_api_calls = 0

                for a in fr_data:
                    s = a.split('\t')
                    if len(s) == 2:
                        # Count only sensitive APIs
                        if s[0] in sensitive_apis_mapping:
                            total_api_calls += int(s[1].strip())
                            nr_api_calls += 1

                        if s[0] == api:
                            this_api_calls = int(s[1].strip())
                            nr_this_api_calls = 1

                for line in scenario_data:
                    if ('true' in line) and (restriction in line):
                        logger.info('Mapped %s -> %s' % (restriction, api))

                        done = False
                        for idx, a in enumerate(result):
                            if a[0] == scenario_file:
                                result[idx][2] += this_api_calls
                                result[idx][4] += nr_this_api_calls
                                result[idx][5] += '\t%s' % api
                                done = True

                        if not done:
                            result.append([scenario_file, total_api_calls, this_api_calls, nr_api_calls, nr_this_api_calls, api])

                        break

for r in result:
    print('%s\t%d\t%d\t%d\t%d\t%s' % (r[0], r[1], r[2], r[3], r[4], r[5]))