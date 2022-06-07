# -*- coding: utf-8 -*-
import numpy as np
import tensorflow as tf
from Tool.Actions import Actions, Directions
class Agent:
    def __init__(self,act_dim,algorithm,e_greed=0.1,e_greed_decrement=0):
        self.act_dim = act_dim
        self.algorithm = algorithm
        self.e_greed = e_greed
        self.e_greed_decrement = e_greed_decrement
        self.Qvalues = {}
        self.QstateList = []
    
    def getQvalue(self, state, action):
        if (state, action) in self.Qvalues:
            return self.Qvalues[(state, action)]
        else:
            return 0.0

    def getLegalActions(self, state):
        return (Actions, Directions)

    def computeValueFromQValues(self, state):
        if len(self.getLegalActions(state)) == 0:
            return None
        else:
            return sorted([(self.getQValue(state, action), action) for action in self.getLegalActions(state)], key = lambda x: x[0], reverse=True)[0][1]

    def computeActionFromQValues(self, state):
        if len(self.getLegalActions(state)) == 0:
            return None
        else:
            return sorted([(self.getQValue(state, action), action) for action in self.getLegalActions(state)], key = lambda x: x[0], reverse=True)[0][1]      
    
    def sample(self, station, soul, hornet_x, hornet_y, player_x, hornet_skill1):
        
        # state = station
        # state = (abs(hornet_x - player_x)+hornet_y, hornet_skill1)
        # state = (manhattan_distance, skill)
        # state should contain hornet_x hornet_y, player_x, player_y, screenshot of hornet.
        state = (int(player_x), int(player_y), int(hornet_x), int(hornet_y))
        # print('current state:', state)

        pred_move, pred_act = self.algorithm.model.predict(state)
        # print(pred_move)
        # print(self.e_greed)
        pred_move = pred_move.numpy()
        pred_act = pred_act.numpy()
        sample = np.random.rand()  
        if sample < self.e_greed:
            move = self.better_move(hornet_x, player_x, hornet_skill1)
        else:
            move = np.argmax(pred_move)
        self.e_greed = max(
            0.03, self.e_greed - self.e_greed_decrement)  

        sample = np.random.rand() 
        if sample < self.e_greed:   # explore
            act = self.better_action(soul, hornet_x, hornet_y, player_x, hornet_skill1)
        else:   # exploit
            act = np.argmax(pred_act)
            if soul < 33:
                if act == 4 or act == 5:
                    pred_act[0][4] = -30
                    pred_act[0][5] = -30
            act = np.argmax(pred_act)

        self.e_greed = max(
            0.03, self.e_greed - self.e_greed_decrement)  
        return move, act
    
    def better_move(self, hornet_x, player_x, hornet_skill1):
        dis = abs(player_x - hornet_x)
        dire = player_x - hornet_x
        if hornet_skill1:
            # run away while distance < 6
            if dis < 6:
                if dire > 0:
                    return 1
                else:
                    return 0
            # do not do long move while distance > 6
            else:
                if dire > 0:
                    return 2
                else:
                    return 3

        if dis < 2.5:
            if dire > 0:
                return 1
            else:
                return 0
        elif dis < 5:
            if dire > 0:
                return 2
            else:
                return 3
        else:
            if dire > 0:
                return 0
            else:
                return 1

    def better_action(self,soul, hornet_x, hornet_y, player_x, hornet_skill1):
        dis = abs(player_x - hornet_x)
        if hornet_skill1:
            if dis < 3:
                return 6
            else:
                return 1
        
        if hornet_y > 34 and dis < 5 and soul >= 33:
            return 4
        
        if dis < 1.5:
            return 6
        elif dis < 5:
            if hornet_y > 32:
                return 6
            else:
                act = np.random.randint(self.act_dim)
                if soul < 33:
                    while act == 4 or act == 5:
                        act = np.random.randint(self.act_dim)
                return act
        elif dis < 12:
            act = np.random.randint(2)
            return 2 + act
        else:
            return 6
                
