import numpy as np
import scipy.special, time, math
import copy
from collections import namedtuple

class Path:
    def __init__(self,line):
        parameters = line.split(' ')
        parameters = list(filter(None, parameters))
        self.id = int(parameters[0])
        parameters.pop(0)
        self.path = [int(parameter) for parameter in parameters]
    def __str__(self):
        message = '\t[ŚCIEŻKA] '+str(self.id)+': '
        for index,link in enumerate(self.path):
            if index<len(self.path)-1: message += str(link) +'-'
            else: message += str(link)
        return message.ljust(25)

class Demand:
    def __init__(self,block,id):
        self.id = id
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
        
        self.flowDistributionCounter = 0
        self.flowDistribution = [0]*self.numberOfPaths
        self.nextFlowDistribution()
        self.numberOfFlowDistributions = scipy.special.binom(self.volume+self.numberOfPaths-1,self.numberOfPaths-1)
    
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
        
    def resetFlowDistributionCounter(self):
        self.flowDistributionCounter = 0
        
    def setFlowOptions(self,flowOptions):
        self.flowOptions = flowOptions
    def __str__(self):
        message = '[ŻĄDANIE] '+str(self.id)+': '+str(self.startNode)+'--'+str(self.endNode)+'\n\tzapotrzebowanie='+str(self.volume)+'\n'
        for index,path in enumerate(self.paths):
            message += str(path) + '-> ' + str(self.flowDistribution[index]) + '\n'
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
        self.capacity = self.pairsInCable*self.lambdas
        
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
        self.bestSolutions = []
        self.F = None
    
    def parse(self,filename):
        file = open(filename)
        content = file.read()
        file.close()
        both  = content.split('-1')
        lines = both[0]
        lines = lines.split('\n')
        
        # links
        self.numberOfLinks = int(lines[0])
        links = lines[1:self.numberOfLinks+1]
        for i,link in enumerate(links):
            self.links.append(Link(link,i+1))
        
        # demands
        lines = both[1]
        lines = lines.split('\n\n')
        lines = list(filter(None, lines))
        self.numberOfDemands = int(lines[0])
        lines.pop(0)
        for id,line in enumerate(lines):
            self.demands.append(Demand(line,id+1))
    
    def saveResultsToFile(self,fileName):
        file = open(fileName,'w')
        linkPart = str(self.numberOfLinks)+'\n'
        for link in self.links:
            linkPart+=str(link.id)+' '+str(link.lambdas)+' '+str(link.pairsInCable)+'\n'
        
        demandPart = str(self.numberOfDemands)+'\n'
        for demand in self.bestSolutions[0]:
            demandFlow = str(demand.id)+' '+str(demand.numberOfPaths)+'\n'
            for index,flow in enumerate(demand.flowDistribution):
                demandFlow+=str(index+1)+' '+str(flow)+'\n'
            demandPart+=demandFlow+'\n'
        
        output = linkPart+'\n'+demandPart
        print('\nPLIK ('+fileName+'):\n','-'*30,'\n',output,'-'*30,sep='')
        file.write(output)
        file.close()
    
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
    
    ############################## ALGORYTM EWOLUCYJNY ##############################
    
    def evolution(self,problem = 'DAP',crossoverProbability=0.75,mutationProbability=0.05,numberOfChromosomes=8):
        """
        link = [load,capacity,lambdas,fibreCost]
        demand = [volume,paths,flows]
        """
        links = [[0,link.capacity,link.lambdas,link.fibreCost] for link in self.links]
        demands = [[demand.volume,demand.paths,[]] for demand in self.demands]
        generation = 0
        population = [self.generateChromosome() for chromosome in range(numberOfChromosomes)]
        print('POPULATION:')
        [print(chromosome) for chromosome in population]


        destinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in population]
        print('DESTINATION',destinationValues)

        # while self.stopCondition(generation):
        #     T = self.reproduction(P)
        #     # O = self.crossover(T,P)
        #     # O = self.mutation(O)
        #     # self.childAnalyse(O,problem,links,demands)
        #     # P = O            
        #     generation+=1
    
    def stopCondition(self,generation):
        if generation<5: return True
        else: return False
    
    def getPopulation(self):
        return [demand.flowDistribution for demand in self.demands]

    def setPopulation(self,P):
        for index,demand in (self.demands):
            demand.flowDistribution=P[index]

    def generateChromosome(self):
        chromosome = []
        for index,gene in enumerate(self.demands):
            randomArray = np.random.randint(0,gene.numberOfPaths,gene.volume)
            chromosome.append([0]*gene.numberOfPaths)
            for value in randomArray:
                chromosome[index][value]+=1
        return chromosome
    
    def destinationFunction(self,P,problem,links,demands):
        if problem == 'DAP': return self.EAcalculateDAP(P,links,demands)
        elif problem == 'DDAP': return self.EAcalculateDDAP(P,links,demands)
    
    def selection(self):
        pass
    
    def crossover(self,T,P):
        pass
    
    def mutation(self,O):
        pass
    
    def reproduction(self,P):
        return 0
    
    def chooseBest(self):
        pass
    
    def EAcalculateDAP(self,P,links,demands):
        # links = copy([[0,link.capacity,link.lambdas,link.fibreCost] for link in self.links])
        links, demands = self.EAsetLoads(P,links,demands)
        # print('-'*30)
        # print('LINKS:',links)
        # for demand in demands:
        #     print('DEMAND')
        #     for index,path in enumerate(demand[1]):
        #         print(path,demand[2][index])
        # print('-'*30)
        F = -float('inf')
        for link in links:
            overload = link[0]-link[1]
            F = max(overload,F)
        # print('F:',F)
        return F
    
    def EAcalculateDDAP(self,P,links,demands):
        links = self.EAsetLoads(P,links,demands)
        F = 0
        for link in links:
            y =math.ceil(link[0]/link[2])
            F += y*link[3]
        return F

    def EAsetLoads(self,chromosome,links,demands):
        for index,demand in enumerate(demands):
            demand[2]=chromosome[index]
        for demandIndex,demand in enumerate(self.demands):
            for index,path in enumerate(demand.paths):
                flow = chromosome[demandIndex][index]
                if flow:
                    for link in path.path:
                        # print('do linku',link,'dodano',flow)
                        links[link-1][0] += flow
                    
        return links,demands

    def BFsetLoads1(self):
        for link in self.links:
            link.load = 0
        for demand in self.demands:
            for index,path in enumerate(demand.paths):
                flow = demand.flowDistribution[index]
                if flow:
                    for link in path.path:
                        self.links[link-1].load += flow


    ############################# ALGORYTM BRUTE FORCE ##############################
    
    def bruteForce(self,problem = 'DAP'):
        self.numberOfSolutions = self.getNumberOfSolutions()
        print('\n  ROZWIĄZAŃ:',self.numberOfSolutions,'\n')
        counter = 0
        F = float('inf')
        while counter <= self.numberOfSolutions:
            if problem == 'DAP': Ftemp = self.BFcalculateDAP()
            elif problem == 'DDAP': Ftemp = self.BFcalculateDDAP()
            if Ftemp < F:
                F = Ftemp
                c = copy.deepcopy(self.demands)
                self.bestSolutions = [c]
            elif Ftemp == F:
                c = copy.deepcopy(self.demands)
                self.bestSolutions.append(c)
            self.demands[0].nextFlowDistribution()
            for index,demand in enumerate(self.demands):
                if demand.flowDistributionCounter > demand.numberOfFlowDistributions:
                    demand.resetFlowDistributionCounter()
                    self.demands[(index+1)%self.numberOfDemands].nextFlowDistribution()
            if not counter%int(self.numberOfSolutions*0.01):
                self.printProgressBar(counter+1,self.numberOfSolutions,suffix='Rozpatrzone przypadki: '+str(counter),decimals=0)
            counter+=1
        self.F = F
        self.printBestSolutions(F,problem)
        self.saveResultsToFile('output/BruteForce'+problem+'.txt')
    
    def BFcalculateDAP(self):
        self.BFsetLoads()
        F = -float('inf')
        for link in self.links:
            overload = link.load-link.capacity
            F = max(overload,F)
        return F
    
    def BFcalculateDDAP(self):
        self.BFsetLoads()
        F = 0
        for link in self.links:
            y =math.ceil(link.load/link.lambdas)
            F += y*link.fibreCost
        return F

    def BFsetLoads(self):
        for link in self.links:
            link.load = 0
        for demand in self.demands:
            for index,path in enumerate(demand.paths):
                flow = demand.flowDistribution[index]
                if flow:
                    for link in path.path:
                        self.links[link-1].load += flow
    
    #################################################################################

    def printBestSolutions(self,F,problem):
        print('\nBrute Force',problem,'\nminF:',F)
        print('Rozwiązań:',len(self.bestSolutions))
        # for solution in self.bestSolutions:
        #     for demand in solution:
        #         print(demand.flowDistribution,end=' ')
        #     print()
    
    def getNumberOfSolutions(self):
        solutions = 1
        for demand in self.demands:
            k = demand.volume
            n = demand.numberOfPaths
            solutions*=scipy.special.binom(k+n-1,n-1)
        return int(solutions)
    
    def getRandomState(self):
        state = np.random.get_state()
    
    def setRandomState(self):
        np.random.random()
    
    def printProgressBar (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 80, fill = '█', printEnd = "\r"):
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
    # n1.bruteForce('DAP')
    # n1.bruteForce('DDAP')
    n1.evolution('DAP')