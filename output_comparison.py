import logging
import os
from math import sqrt

logger = logging.getLogger()


class OutputComparison(object):
    initial_exploration_dir = None

    def __init__(self, initial_exploration_dir):
        self.initial_exploration_dir = initial_exploration_dir

    @staticmethod
    def execution_crashed(exploration_dir):
        """
        Check is an execution was successful
        :param exploration_dir: Directory where the exploration results are stored
        :return: If the exploration crashed during execution or not
        """
        aggregate_results_file = os.path.join(exploration_dir, 'aggregate_stats.txt')

        assert os.path.exists(aggregate_results_file)

        f = open(aggregate_results_file)
        data = f.readlines()
        f.close()

        # Droidmate return
        return not 'N/A (lack of DeviceException)' in data[-1]

    @staticmethod
    def observed_explored(exploration_dir):
        """
        Check is an execution was successful
        :param exploration_dir: Directory where the exploration results are stored
        :return: Get the number of explored/observed widgets
        """
        aggregate_results_file = os.path.join(exploration_dir, 'aggregate_stats.txt')

        assert os.path.exists(aggregate_results_file)

        f = open(aggregate_results_file)
        data = f.readlines()
        f.close()

        # If it has two lines
        if len(data) > 1:
            tmp = data[1].split('\t')
            unique_observed = tmp[5]
            unique_explored = tmp[6]

            return '%s,%s' % (unique_observed, unique_explored)

        return '0,0'

    @staticmethod
    def __equal_observed_explored(first, second):
        tmp = first.split(',')
        first_unique_observed = int(tmp[0])
        first_unique_explored = int(tmp[1])
        tmp = second.split(',')
        second_unique_observed = int(tmp[0])
        second_unique_explored = int(tmp[1])

        #d(E_0, E_x) = \sqrt{(expl(E_0) - expl(E_x)) ^ 2 + (obs(E_0) - obs(E_x)) ^ 2}
        # Comparing to ROOT
        dist1 = sqrt(pow(first_unique_explored, 2) + pow(first_unique_observed, 2))
        dist2 = sqrt(pow(second_unique_explored, 2) + pow(second_unique_observed, 2))

        # return abs(dist1 - dist2) < (dist1 * 0.05)
        # return abs(dist1 - dist2) < (dist1 * 0.10)
        # return abs(dist1 - dist2) < (dist1 * 0.15)
        # return abs(dist1 - dist2) < (dist1 * 0.20)
        # return abs(dist1 - dist2) < (dist1 * 0.30)
        # return abs(dist1 - dist2) < (dist1 * 0.40)
        return abs(dist1 - dist2) < (dist1 * 0.50)

    @staticmethod
    def __write_results_file(data, output_dir, name):
        file_name = os.path.join(output_dir, name)
        f = open(file_name, 'w')

        for item in data:
            s = ''
            for t in item:
                s += str(t) + '\t'
            f.write(s + '\n')

        f.close()

    @staticmethod
    def __equal_apk_did_not_crash(first, second):
        return first == second

    def __compare(self, current_exploration_dir, apks, evaluation_method, comparison_method, output_file_name):
        """
        Compare all exploration contained in a folder with their base explorations. Two explorations are considered
        equivalent if both did not crash
        :param current_exploration_dir: Base directory containing all explorations to be evaluated
        :param apks: List of APKs that were explored
        :param evaluation_method: Pointer to the method that will be used to evalute an exploration
        :param comparison_method: Ponter to the method that will be used to compare two explorations
        :param output_file_name: Name of the output file
        :return: List of APKs and equivalence information (APK [APKAdapter], scenario [String], first result, second
        result, equivalent [Boolean])
        """
        result = []

        for apk in apks:
            logger.debug("Evaluating results for %s", apk)

            apk_dir_name = apk.get_apk_name_as_directory_name()

            # The the initial exploration result
            first_run_dir = os.path.join(self.initial_exploration_dir, apk_dir_name)
            #first_run_dir = os.path.join('C:\\Users\\natan_000\\Desktop\\Saarland\\repositories\\automatic-permission-tightening\\data\\exploration\\first-run', apk_dir_name)
            #current_exploration_dir = 'C:\\Users\\natan_000\\Desktop\\Saarland\\repositories\\automatic-permission-tightening\\data\\app_did_not_crash\\exploration\\8-api-blocked'

            if not os.path.exists(first_run_dir):
                logger.error('Initial exploration missing for APK (%s)', apk)
                result.append([apk, None, False, False, False])
            else:
                # Get the first exploration result
                first_run_result = evaluation_method(first_run_dir)

                # Get the executed scenarios
                scenario_list_dir = os.path.join(current_exploration_dir, apk_dir_name)
                if os.path.exists(scenario_list_dir) and os.path.isdir(scenario_list_dir):
                    for scenario in os.listdir(scenario_list_dir):
                        scenario_dir = os.path.join(scenario_list_dir, scenario)

                        scenario_result = evaluation_method(scenario_dir)

                        equivalent_results = comparison_method(first_run_result, scenario_result)
                        apk_dir = apk.get_apk_name_as_directory_name()
                        result.append([apk_dir, scenario, first_run_result, scenario_result, equivalent_results])

        OutputComparison.__write_results_file(result, current_exploration_dir, output_file_name)
        return result

    def compare_with_apk_did_not_crash(self, current_exploration_dir, apks):
        """
        Compare all exploration contained in a folder with their base explorations. Two explorations are considered
        equivalent if both did not crash
        :param current_exploration_dir: Base directory containing all explorations to be evaluated
        :param apks: List of APKs that were explored
        :return: List of APKs and equivalence information (APK [APKAdapter], scenario [String], first result, second
        result, equivalent [Boolean])
        """
        return self.__compare(current_exploration_dir, apks, OutputComparison.execution_crashed,
                              OutputComparison.__equal_apk_did_not_crash, 'app_crashed_comp_results.txt')


    def compare_with_number_of_widgets_observed_explored(self, current_exploration_dir, apks):
        """
        Compare all exploration contained in a folder with their base explorations. Two explorations are considered
        equivalent if they saw a similar (5% variation) number of widgets
        :param current_exploration_dir: Base directory containing all explorations to be evaluated
        :param apks: List of APKs that were explored
        :return: List of APKs and equivalence information (APK [APKAdapter], scenario [String], first result, second
        result, equivalent [Boolean])
        """
        return self.__compare(current_exploration_dir, apks, OutputComparison.observed_explored,
                              OutputComparison.__equal_observed_explored, 'obs_expl_comp_results.txt')
