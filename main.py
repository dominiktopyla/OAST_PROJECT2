import numpy as np
import scipy



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
    def __str__(self):
        message = '[ŻĄDANIE]: '+str(self.startNode)+'--'+str(self.endNode)+'\n\tzapotrzebowanie='+str(self.volume)+'\n'
        for path in self.paths:
            message += str(path) + '\n'
        return message

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
        self.numberOfDemands = lines[0]
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
        F = float('inf')
        numberOfPaths = 3
        numberOfFlows = 4
        x = [[None]*numberOfPaths]*numberOfFlows
        self.rec(1,1,self.h(1),x)
    
    
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
    
    def numberOfSolutions(self,network):
        solutions = 1
        for demand in network.demands:
            newton = self.Newton(demand.volume,demand.numberOfPaths)
            print(newton)
            solutions*=newton
        return solutions
    
    def Newton(self,n,k):
        newton = float(1)
        for i in range(1,k+1):
            newton = newton*(n-i+1)/i
        return newton
    
    #################################################################################
    #################################################################################
    #################################################################################
    
    def getRandomState(self):
        state = np.random.get_state()
    
    def setRandomState(self):
        np.random.random()


if __name__ == "__main__":
    n1 = Network()
    n1.parse('input/net4.txt')
    n1.show()
    
    # print('ROZWIĄZAŃ:',numberOfSolutions(n1))
    