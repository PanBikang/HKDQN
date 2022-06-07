from Tool.WindowsAPI import key_check
import time


# check whether a game is end
def is_end(next_self_blood, min_hp, next_boss_blood, boss_blood):
    if next_self_blood ==9 and min_hp <= 3:    
        return True
    elif next_boss_blood - boss_blood > 200:   
        return True
    return False

# get mean score of a reward seq
def mean(d):
    t = 0
    for i in d:
        t += i
    return t / len(d)

# count play hp change, and give reward 
def count_self_reward(next_self_blood, self_hp):
    if next_self_blood - self_hp < 0:
        return 11 * (next_self_blood - self_hp)
    return 0

# count boss hp change, and give reward 
def count_boss_reward(next_boss_blood, boss_blood):
    if next_boss_blood -  boss_blood < 0:
        return int((boss_blood - next_boss_blood)/9)
    return 0

def direction_reward(move, player_x, hornet_x):
    dire = 0
    s = 0
    dis = 0
    base = 5
    if abs(player_x - hornet_x) < 2.5:
        dis = -1
    else:
        dis = 1
    if player_x - hornet_x > 0:
        s = -1
    else:
        s = 1
    if move == 0 or move == 2:
        dire = -1
    else:
        dire = 1

    return dire * s * dis * base


def distance_reward(move, next_player_x, next_hornet_x):
    if abs(next_player_x - next_hornet_x) < 2.5:
        return -6
    elif abs(next_player_x - next_hornet_x) < 4.8:
        return 4
    else:
        if move < 2:
            return 4
        else:
            return -2

def move_judge(self_blood, next_self_blood, player_x, next_player_x, hornet_x, next_hornet_x, move, hornet_skill1):
    # reward = count_self_reward(next_self_blood, self_blood)
    # if reward < 0:
    #     return reward

    
    if hornet_skill1:
        # run away while distance < 5
        if abs(player_x - hornet_x) < 6:
            # change direction while hornet use skill
            if move == 0 or move == 2:
                dire = 1
            else:
                dire = -1
            if player_x - hornet_x > 0:
                s = -1
            else:
                s = 1
            # if direction is correct and use long move
            if dire * s == 1 and move < 2:
                return -10
        # do not do long move while distance > 5
        else:
            if move >= 2:
                return -10
        return -30

    dis = abs(player_x - hornet_x)
    dire = player_x - hornet_x
    if move == 0:
        if (dis > 5 and dire > 0) or (dis < 2.5 and dire < 0):
            return -10
    elif move == 1:
        if (dis > 5 and dire < 0) or (dis < 2.5 and dire > 0):
            return -10
    elif move == 2:
        if dis > 2.5 and dis < 5 and dire > 0:
            return -10
    elif move == 3:
        if dis > 2.5 and dis < 5 and dire < 0:
            return -10
            
        
    # reward = direction_reward(move, player_x, hornet_x) + distance_reward(move, player_x, hornet_x)
    return -30







def act_skill_reward(hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x):
    skill_reward = -3
    if hornet_skill1:
        if action == 2 or action == 3:
            skill_reward -= 5
    elif  next_hornet_y >34 and abs(next_hornet_x - next_player_x) < 5:
        if action == 4:
            skill_reward += 2
    return skill_reward

def act_distance_reward(action, next_player_x, next_hornet_x, next_hornet_y):
    distance_reward = -2
    if abs(next_player_x - next_hornet_x) < 12:
        if abs(next_player_x - next_hornet_x) > 6:
            if action >= 2 and action <= 3:
                # distance_reward += 0.5
                pass
            elif next_hornet_y < 29 and action == 6:
                distance_reward -= 3
        else:
            if action >= 2 and action <= 3:
                distance_reward -= 0.5
    else:
        if action == 0 and action == 1:
            distance_reward -= 3
        elif action == 6:
            distance_reward += 1
    return distance_reward

# JUDGEMENT FUNCTION, write yourself
def action_judge(boss_blood, next_boss_blood, self_blood, next_self_blood, next_player_x, next_hornet_x,next_hornet_y, action, hornet_skill1):
    # Player dead
    if next_self_blood <= 0 and self_blood != 9:    
        skill_reward = act_skill_reward(hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)
        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            if reward > 0:
                reward *= 1.5
            else:
                reward = float(reward / 1.5)
        elif action == 5:
            if reward > 0:
                reward *= 0.5
            else:
                reward = float(reward / 0.5)
        done = 1
        return reward, done

    #boss dead
    elif next_boss_blood <= 0 or next_boss_blood > 900:   
        skill_reward = act_skill_reward(hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)
        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            if reward > 0:
                reward *= 1.5
            else:
                reward = float(reward / 1.5)
        elif action == 5:
            if reward > 0:
                reward *= 0.5
            else:
                reward = float(reward / 0.5)
        done = 2
        return reward, done
    # playing
    else:
        skill_reward = act_skill_reward(hornet_skill1, action, next_hornet_x, next_hornet_y, next_player_x)
        distance_reward = act_distance_reward(action, next_player_x, next_hornet_x, next_hornet_y)
        self_blood_reward = count_self_reward(next_self_blood, self_blood)
        boss_blood_reward = count_boss_reward(next_boss_blood, boss_blood)

        reward = self_blood_reward + boss_blood_reward + distance_reward + skill_reward
        if action == 4:
            if reward > 0:
                reward *= 1.5
            else:
                reward = float(reward / 1.5)
        elif action == 5:
            if reward > 0:
                reward *= 0.5
            else:
                reward = float(reward / 0.5)
        done = 0
        return reward, done

# Paused training
def pause_game(paused):
    op, d = key_check()
    if 'T' in op:
        if paused:
            paused = False
            print('start game')
            time.sleep(1)
        else:
            paused = True
            print('pause game')
            time.sleep(1)
    if paused:
        print('paused')
        while True:
            op, d = key_check()
            # pauses game and can get annoying.
            if 'T' in op:
                if paused:
                    paused = False
                    print('start game')
                    time.sleep(1)
                    break
                else:
                    paused = True
                    time.sleep(1)
    return paused


class Counter(dict):
    """
    A counter keeps track of counts for a set of keys.

    The counter class is an extension of the standard python
    dictionary type.  It is specialized to have number values
    (integers or floats), and includes a handful of additional
    functions to ease the task of counting data.  In particular,
    all keys are defaulted to have value 0.  Using a dictionary:

    a = {}
    print a['test']

    would give an error, while the Counter class analogue:

    >>> a = Counter()
    >>> print a['test']
    0

    returns the default 0 value. Note that to reference a key
    that you know is contained in the counter,
    you can still use the dictionary syntax:

    >>> a = Counter()
    >>> a['test'] = 2
    >>> print a['test']
    2

    This is very useful for counting things without initializing their counts,
    see for example:

    >>> a['blah'] += 1
    >>> print a['blah']
    1

    The counter also includes additional functionality useful in implementing
    the classifiers for this assignment.  Two counters can be added,
    subtracted or multiplied together.  See below for details.  They can
    also be normalized and their total count and arg max can be extracted.
    """

    def __getitem__(self, idx):
        self.setdefault(idx, 0)
        return dict.__getitem__(self, idx)

    def incrementAll(self, keys, count):
        """
        Increments all elements of keys by the same count.

        >>> a = Counter()
        >>> a.incrementAll(['one','two', 'three'], 1)
        >>> a['one']
        1
        >>> a['two']
        1
        """
        for key in keys:
            self[key] += count

    def argMax(self):
        """
        Returns the key with the highest value.
        """
        if len(list(self.keys())) == 0:
            return None
        all = list(self.items())
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def sortedKeys(self):
        """
        Returns a list of keys sorted by their values.  Keys
        with the highest values will appear first.

        >>> a = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> a['third'] = 1
        >>> a.sortedKeys()
        ['second', 'third', 'first']
        """
        sortedItems = list(self.items())

        def compare(x, y): return sign(y[1] - x[1])
        sortedItems.sort(key=functools.cmp_to_key(compare))
        return [x[0] for x in sortedItems]

    def totalCount(self):
        """
        Returns the sum of counts for all keys.
        """
        return sum(self.values())

    def normalize(self):
        """
        Edits the counter such that the total count of all
        keys sums to 1.  The ratio of counts for all keys
        will remain the same. Note that normalizing an empty
        Counter will result in an error.
        """
        total = float(self.totalCount())
        if total == 0:
            return
        for key in list(self.keys()):
            self[key] = self[key] / total

    def divideAll(self, divisor):
        """
        Divides all counts by divisor
        """
        divisor = float(divisor)
        for key in self:
            self[key] /= divisor

    def copy(self):
        """
        Returns a copy of the counter
        """
        return Counter(dict.copy(self))

    def __mul__(self, y):
        """
        Multiplying two counters gives the dot product of their vectors where
        each unique label is a vector element.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['second'] = 5
        >>> a['third'] = 1.5
        >>> a['fourth'] = 2.5
        >>> a * b
        14
        """
        sum = 0
        x = self
        if len(x) > len(y):
            x, y = y, x
        for key in x:
            if key not in y:
                continue
            sum += x[key] * y[key]
        return sum

    def __radd__(self, y):
        """
        Adding another counter to a counter increments the current counter
        by the values stored in the second counter.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> a += b
        >>> a['first']
        1
        """
        for key, value in list(y.items()):
            self[key] += value

    def __add__(self, y):
        """
        Adding two counters gives a counter with the union of all keys and
        counts of the second added to counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a + b)['first']
        1
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] + y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = y[key]
        return addend

    def __sub__(self, y):
        """
        Subtracting a counter from another gives a counter with the union of all keys and
        counts of the second subtracted from counts of the first.

        >>> a = Counter()
        >>> b = Counter()
        >>> a['first'] = -2
        >>> a['second'] = 4
        >>> b['first'] = 3
        >>> b['third'] = 1
        >>> (a - b)['first']
        -5
        """
        addend = Counter()
        for key in self:
            if key in y:
                addend[key] = self[key] - y[key]
            else:
                addend[key] = self[key]
        for key in y:
            if key in self:
                continue
            addend[key] = -1 * y[key]
        return addend
