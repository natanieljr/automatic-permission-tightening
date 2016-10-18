import logging
import os

logger = logging.getLogger()


class OutputComparison(object):
    base_exploration_dir = None

    def __init__(self, base_exploration_dir):
        self.base_exploration_dir = base_exploration_dir

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

    def compare_results_using_apk_did_not_crash_strategy(self, initial_exploration_dir, current_exploration_dir, apks):
        """
        Compare all exploration contained in a folder with their base explorations. Two explorations are considered
        equivalent if both did not crash
        :param initial_exploration_dir: Directory containing the results of the first exploration
        :param current_exploration_dir: Base directory containing all explorations to be evaluated
        :param apks: List of APKs that were explored
        :return: List of APKs and equivalence information (APK [APKAdapter], scenario [String], equivalent [Boolean])
        """
        result = []

        for apk in apks:
            logger.debug("Evaluating results for %s", apk)

            apk_dir_name = apk.get_apk_name_as_directory_name()

            # The the initial exploration result
            first_run_dir = os.path.join(initial_exploration_dir, apk_dir_name)

            if (not os.path.exists(first_run_dir)):
                logger.error('Initial exploration missing for APK (%s)', apk)
                result.append([apk, None, False])
            else:
                # Get the first exploration result
                first_run_result = OutputComparison.execution_crashed(first_run_dir)

                # Get the executed scenarios
                scenario_list_dir = os.path.join(current_exploration_dir, apk_dir_name)
                if os.path.exists(scenario_list_dir) and os.path.isdir(scenario_list_dir):
                    for scenario in os.listdir(scenario_list_dir):
                        scenario_dir = os.path.join(scenario_list_dir, scenario)

                        scenario_result = OutputComparison.execution_crashed(scenario_dir)

                        equivalent_results = (first_run_result == scenario_result)
                        result.append([apk, scenario, equivalent_results])

        return result
