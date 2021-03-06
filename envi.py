import time
from os.path import exists
import gym
from utils.KubeResources import *
from algos.GeneticSched import *


class CloudEnv:
    def __init__(self):
        """
        Action space : discrete : Genetic, Kube default scheduler
        Observation space / same state space : we can maybe start with the nb of tasks and their cpu usage and the
        available nodes and maybe later we can alter the nodes resources

        """
        super(CloudEnv, self).__init__()
        self.episode_steps = 0
        self.last_metrics = None
        self.same_results = 0
        self.actions = {0: 'genetic', 1: 'scheduler-round-robin'}

    def step(self, action):
        """
        for each step run one scheduling algo and wait a bit for results and get them and delete pods and restart them
        maybe each time we re-run we run random number of replicas set so that we can vary and change the
        agent's experience
        :param action:
        :return:
        """
        reconfigure(self.actions[action])
        time.sleep(5)
        if self.actions[action] == 'genetic':
            schedule()
        time.sleep(5)
        metrics = resources()  # [1] for training and without for testing
        reward = self.reward(metrics)
        done = self.termination()
        next_state = get_nextstate()
        self.episode_steps = self.episode_steps + 1
        # return metrics  # for testing
        return action, next_state, reward, done  # for training

    def reset(self, new_epi):
        if new_epi:
            self.last_metrics = None
        state = reset(new_epi)
        return state

    def termination(self):
        """
        check maybe the number of steps of our agent if we attended that time step we stop
        :return:
        """
        # what we could do this get the number of
        if self.same_results == 2:
            self.episode_steps = 0
            return True
        return False

    def reward(self, metrics):
        """
        what is our reward function. this a prob for now
        maybe try one time get the actual measurements of that cpu of the node
        and on the next
        Later check the condition of nodes if one pod got effected he gets --
        :return:
        """
        if self.last_metrics is None:
            self.same_results = 0
        else:
            if metrics[0] <= self.last_metrics[0] or metrics[1] <= self.last_metrics[1]:
                self.same_results = self.same_results + 1
        self.last_metrics = metrics
        return 1 / (metrics[0] + metrics[-1])  ## sum of all used resources

        # if self.episode_steps == 0:  # can't compare til we have two time steps
        #   reward = 1
        #   self.same_results = 0
        #   self.last_metrics = metrics
        # else:
        # #exec_time, imbalance_deg = metrics[0], metrics[1]
        # if imbalance_deg <= self.last_metrics[1]:
        #     if exec_time <= self.last_metrics[0]:
        #         reward = 5
        #         self.same_results = 0
        #     else:
        #         reward = 3
        #         self.same_results += 1
        # else:
        #     if exec_time <= self.last_metrics[0]:
        #         reward = 3
        #         self.same_results += 1
        #     else:
        #         reward = -2  # worst case scenario
        #         self.same_results = 0
        # self.last_metrics = metrics
        # if metrics <= self.last_metrics:
        #   reward = 3
        #   self.same_results += 1
        # else:
        # {    reward = -1
        #     self.same_results = 0
        # self.last_metrics = metrics
        # return reward
