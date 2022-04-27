import numpy as np
import scipy.special



class Path:
    def __init__(self,line):
        parameters = line.split(' ')
        parameters = list(filter(None, parameters))
        self.id = int(parameters[0])
        parameters.pop(0)
        self.path = parameters
    def __str__(self):
        message = '\t[ŚCIEŻKA] '+str(self.id)+': '
        for index,node in enumerate(self.path):
            if index<len(self.path)-1: message += node +'-'
            else: message += node
        return message

class Demand:
    def __init__(self,block):
        lines = block.split('\n')
        parameters = lines[0].split(' ')
        self.startNode = int(parameters[0])
        self.endNode = int(parameters[1])
        self.volume = int(parameters[2])
        self.numberOfPaths = int(lines[1])
        self.paths = []
        paths = lines[2:self.numberOfPaths+2]
        for path in paths:
            self.paths.append(Path(path))    
        ################ BRUTE FORCE ################
        self.flowDistributionCounter = 0
        self.flowDistribution = [0]*self.numberOfPaths
        self.nextFlowDistribution()
        self.numberOfFlowDistributions = scipy.special.binom(self.volume+self.numberOfPaths-1,self.volume)
    
    def nextFlowDistribution(self):
        while True:
            self.flowDistribution[0]+=1
            for index,flow in enumerate(self.flowDistribution):
                if flow > self.volume:
                    self.flowDistribution[index]=0
                    self.flowDistribution[(index+1)%self.numberOfPaths]+=1
            if sum(self.flowDistribution) == self.volume:
                self.flowDistributionCounter+=1
                break
        #############################################    
    def setFlowOptions(self,flowOptions):
        self.flowOptions = flowOptions
    def __str__(self):
        message = '[ŻĄDANIE]: '+str(self.startNode)+'--'+str(self.endNode)+'\n\tzapotrzebowanie='+str(self.volume)+'\n'
        for path in self.paths:
            message += str(path) + '\n'
        return message
# '1 2 3 \n3 \n1 1 \n2 2 3 \n3 2 5 4 '
# while d.flowDistributionCounter == d.numberOfFlowDistributions: d.nextFlowDistribution()

class Link:
    def __init__(self,line,id):
        parameters = line.split(' ')
        self.id = id
        self.startNode = int(parameters[0])
        self.endNode = int(parameters[1])
        self.pairsInCable = int(parameters[2])
        self.fibreCost = int(parameters[3])
        self.lambdas = int(parameters[4])
        self.load = 0
    def __str__(self):
        return '[POŁĄCZENIE] '+str(self.id)+': '+str(self.startNode)\
            +'--'+str(self.endNode)\
            +',\tpary='+str(self.pairsInCable)\
            +',\tkoszt='+str(self.fibreCost)\
            +',\tlambdy='+str(self.lambdas)

class Network:
    def __init__(self):
        self.numberOfLinks = None
        self.links = []
        self.numberOfDemands = None
        self.demands = []
    
    def parse(self,filename):
        file = open(filename)
        content = file.read()
        file.close()
        both  = content.split('-1')
        lines = both[0]
        lines = lines.split('\n')
        
        # number of links
        self.numberOfLinks = int(lines[0])
        
        # links
        links = lines[1:self.numberOfLinks+1]
        
        for i,link in enumerate(links):
            self.links.append(Link(link,i+1))
        
        # demands
        lines = both[1]
        lines = lines.split('\n\n')
        lines = list(filter(None, lines))
        self.numberOfDemands = int(lines[0])
        lines.pop(0)
        for line in lines:
            self.demands.append(Demand(line))
    
    def show(self):
        print('-'*70)
        print(' '*30,'PARAMETRY')
        print('-'*70)
        print('Liczba połączeń:',self.numberOfLinks,'\n')
        [print(link) for link in self.links]
        print('-'*70)
        print('Liczba żądań:',self.numberOfDemands,'\n')
        [print(demand) for demand in self.demands]
        print('-'*70)

    def calculateLinkLoads(self):
        for demand in self.demands:
            for path in demand.paths:
                for link in path.path:
                    self.links[int(link)-1].load = self.links[int(link)-1].load + int(demand.volume)

# for demand in n1.demands:
#     for path in demand.paths:
#         for link in path.path:
#             n1.links[int(link)-1].load = n1.links[int(link)-1].load + int(demand.volume)

# for link in n1.links:
#     print(link.load)

    #################################################################################
    ############################## ALGORYTM EWOLUCYJNY ##############################
    #################################################################################
    
    def evolution(self):
        pass
    
    def stopCondition(self):
        return True
    
    def generatePopulation(self):
        pass
    
    def childAnalyse(self):
        pass
    
    def selection(self):
        pass
    
    def crossover(self):
        pass
    
    def mutation(self):
        pass
    
    def chooseBest(self):
        pass
    
    #################################################################################
    ################################## BRUTE FORCE ##################################
    #################################################################################
    
    def bruteForce(self):
        self.numberOfSolutions = self.getNumberOfSolutions()
        print('ROZWIĄZAŃ:',self.numberOfSolutions)
        
        
        
        
        # for index,demand in enumerate(self.demands):
        #     flowOptions = self.getFlowCombinations(demand.volume,demand.numberOfPaths)
        #     demand.setFlowOptions(flowOptions)
        #     self.printProgressBar(index+1,self.numberOfDemands,suffix='Generowanie przypadków podziału przepływności')
        
        # F = float('inf')
        # numberOfPaths = 3
        # numberOfFlows = 4
        # x = [[None]*numberOfPaths]*numberOfFlows
        # self.rec(1,1,self.h(1),x)
    
    
    def rec(self,demandId,pathId,lefth,x):
        # lefth -  remaining part of current demand’s volume
        # x - solution, two dimensional array of path-flows
        if pathId == self.P(demandId):
            x[demandId][pathId]=lefth
            if demandId < self.numberOfDemands:
                self.rec(demandId+1,1,self.h(demandId+1),x)
            else:
                print(x)
        else:
            for parth in range(0,lefth):
                x[demandId][pathId]
                self.rec(demandId,pathId+1,lefth-parth,x)
    
    def P(self,curd):
        #number of demands paths
        return True    
    
    def h(self,curd):
        #demands Volume
        pass
    
    def getFlowCombinations(self,flowSum,paths):
        x = [0]*paths
        l = []
        for i in range(pow(flowSum+1,paths)):
            if sum(x) == flowSum:
                l.append(x)
            x[0]+=1
            for i in range(len(x)):
                if x[len(x)-1] > flowSum:
                    return l
                if x[i] > flowSum:
                    x[i] = 0
                    x[i+1]+=1
        # return [[int(digit) for digit in str(number).zfill(paths)] for number in range(1,pow(10,paths+1)-1) if sum([int(digit) for digit in str(number)])==flowSum]
            
        
    
    def getNumberOfSolutions(self):
        solutions = 1
        for demand in self.demands:
            k = demand.volume
            n = demand.numberOfPaths
            solutions*=scipy.special.binom(k+n-1,k)
        return int(solutions)
    
    #################################################################################
    #################################################################################
    #################################################################################
    
    def getRandomState(self):
        state = np.random.get_state()
    
    def setRandomState(self):
        np.random.random()
        
    def printProgressBar (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + ' ' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        if iteration == total: 
            print()




    
    
    
    
if __name__ == "__main__":
    n1 = Network()
    n1.parse('input/net4.txt')
    # n1.show()
    n1.bruteForce()