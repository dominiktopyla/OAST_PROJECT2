from hashlib import new
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
    def __init__(self,inputFileName,outputFileName):
        self.numberOfLinks = None
        self.links = []
        self.numberOfDemands = None
        self.demands = []
        self.bestSolutions = []
        self.F = None
        self.inputFileName = inputFileName
        self.outputFileName = outputFileName
        self.stopConditionType=None
        self.stopConditionValue=None
        self.initTime=None
        self.mutationCounter=0
        self.bestForNCounter=0
        self.saveAllBFSolutions=False

    def parse(self):
        file = open('input/'+self.inputFileName)
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
    
    def saveResultsToFile(self):
        file = open('output/'+self.outputFileName,'w')
        linkPart = str(self.numberOfLinks)+'\n'
        for link in self.links:
            linkPart+=str(link.id)+' '+str(link.lambdas)+' '+str(link.pairsInCable)+'\n'
        
        demandPart = str(self.numberOfDemands)+'\n'
        for index,solution in enumerate(self.bestSolutions):
            if index == 0 or self.saveAllBFSolutions:
                demandPart+='\n'
                for demand in solution:
                    demandFlow = str(demand.id)+' '+str(demand.numberOfPaths)+'\n'
                    for index,flow in enumerate(demand.flowDistribution):
                        demandFlow+=str(index+1)+' '+str(flow)+'\n'
                    demandPart+=demandFlow+'\n'
        
        output = linkPart+'\n'+demandPart
        print('\nPLIK ('+self.outputFileName+'):\n','-'*30,'\n',output,'-'*30,sep='')
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
    
    def evolution(self,problem,crossoverProbability,mutationProbability,numberOfChromosomes,stopConditionType,stopConditionValue):
        """
        link = [load,capacity,lambdas,fibreCost]
        demand = [volume,paths,flows]
        """
        self.stopConditionType = stopConditionType
        self.stopConditionValue = stopConditionValue
        if stopConditionValue == 'time': self.initTime = time.time()
        links = [[0,link.capacity,link.lambdas,link.fibreCost] for link in self.links]
        demands = [[demand.volume,demand.paths,[]] for demand in self.demands]
        generation = 0
        population = [self.generateChromosome() for chromosome in range(numberOfChromosomes)]
        destinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in population]
        F=min(destinationValues)
        while self.stopCondition(generation):
            print('POPULATION: F=',F,'\tgeneracja:',generation)
            [print(chromosome,' F:',destinationValues[index]) for index,chromosome in enumerate(population)]
            temporaryPopulation = self.reproduction(population,destinationValues)
            print('TMP POPULATION:')
            [print(chromosome) for chromosome in temporaryPopulation]
            temporaryPopulation = self.crossover(temporaryPopulation,crossoverProbability)
            print('AFTER CROSSOVER:')
            [print(chromosome) for chromosome in temporaryPopulation]
            temporaryPopulation = self.mutation(temporaryPopulation,mutationProbability)
            print('AFTER MUTATION:')
            [print(chromosome) for chromosome in temporaryPopulation]
            bestPopulation = self.chooseBest(population,temporaryPopulation,numberOfChromosomes,problem,links,demands)
            print('BEST POPULATION:')
            [print(chromosome) for chromosome in bestPopulation]
            population = bestPopulation
            
            destinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in population]
            if F == min(destinationValues):
                self.bestForNCounter+=1
            else: self.bestForNCounter=0
            # if min(destinationValues)<F:
            #     F = min(destinationValues)
            #     print('POPULATION: F=',F,'\tgeneracja:',generation)
            #     [print(chromosome,' F:',destinationValues[index]) for index,chromosome in enumerate(population)]  
            print('-'*70)
            generation+=1
        destinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in population]
        print('LAST POPULATION: F=',min(destinationValues),'\tgeneracja:',generation)
        [print(chromosome,' F:',destinationValues[index]) for index,chromosome in enumerate(population)]

        bestChromosome = population[np.argmin(destinationValues)]
        self.bestSolutions = [self.demands]
        self.setPopulation(bestChromosome)
        self.saveResultsToFile()
        
    def success(self,successProbability):
        if np.random.random()<successProbability: return True
        else: return False

    def stopCondition(self,generation):
        if self.stopConditionType == 'time':
            if time.time()-self.initTime<self.stopConditionValue: return True
            else: return False
        elif self.stopConditionType == 'mutations':
            if self.mutationCounter<self.stopConditionValue: return True
            else: return False
        elif self.stopConditionType == 'generations':
            if generation<self.stopConditionValue: return True
            else: return False
        elif self.stopConditionType == 'bestForN':
            if self.bestForNCounter<self.stopConditionValue: return True
            else: return False
        
    def getPopulation(self):
        return [demand.flowDistribution for demand in self.demands]

    def setPopulation(self,chromosome):
        for index,demand in enumerate(self.demands):
            demand.flowDistribution=chromosome[index]

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
    
    def crossover(self,temporaryPopulation,crossoverProbability):
        childs = []
        for index in range(0,len(temporaryPopulation),2):
            if index == len(temporaryPopulation)-1:
                childs.append(temporaryPopulation[index])
            else:
                parenta = temporaryPopulation[index]
                parentb = temporaryPopulation[index+1]
                if self.success(crossoverProbability):
                    r = np.random.randint(0,self.numberOfDemands)
                    childa = copy.copy(parenta)
                    childb = copy.copy(parentb)
                    childa[r:] = parentb[r:]
                    childb[r:] = parenta[r:]
                    childs.append(childa)
                    childs.append(childb)
                else:
                    childs.append(parenta)
                    childs.append(parentb)
        
        return childs
    
    def mutation(self,temporaryPopulation,mutationProbability):
        for chromosome in temporaryPopulation:
            for gene in chromosome:
                if self.success(mutationProbability):
                    self.mutationCounter+=1
                    vector = list(range(0,len(gene)))
                    r1 = np.random.randint(0,len(gene))
                    vector.pop(r1)
                    r2 = np.random.randint(0,len(gene)-1)
                    r2 = vector[r2]
                    tmp = gene[r1]
                    gene[r1]=gene[r2]
                    gene[r2]=tmp
        return temporaryPopulation
            
    def reproduction(self,population,destinationValues):
        temporaryPopulation = []
        s = sum(destinationValues)
        destinationValues = [value-s for value in destinationValues] 
        s = sum(destinationValues)
        destinationProbabilities = [value/s for value in destinationValues] 
        for index in range(1,len(destinationProbabilities)):
            destinationProbabilities[index]+=destinationProbabilities[index-1]
        for chromosome in population:
            r = np.random.random()
            for index,probability in enumerate(destinationProbabilities):
                if r < probability:
                    temporaryPopulation.append(copy.copy(population[index]))
                    break
        return temporaryPopulation
    


    def chooseBest(self,population,temporaryPopulation,numberOfChromosomes,problem,links,demands):
        destinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in population]
        temporaryDestinationValues = [copy.copy(self.destinationFunction(chromosome,problem,copy.deepcopy(links),copy.copy(demands))) for chromosome in temporaryPopulation]
        population+=temporaryPopulation
        destinationValues+=temporaryDestinationValues
        newPopulation = []
        for index in range(numberOfChromosomes):
            minindex = np.argmin(destinationValues)
            newPopulation.append(copy.copy(population[minindex]))
            destinationValues[minindex]=float('inf')
        return newPopulation

    
    def EAcalculateDAP(self,P,links,demands):
        links, demands = self.EAsetLoads(P,links,demands)
        F = -float('inf')
        for link in links:
            overload = link[0]-link[1]
            F = max(overload,F)
        return F
    
    def EAcalculateDDAP(self,P,links,demands):
        links, demands = self.EAsetLoads(P,links,demands)
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
                        links[link-1][0] += flow
                    
        return links,demands

    ############################# ALGORYTM BRUTE FORCE ##############################
    
    def bruteForce(self,problem = 'DAP',saveAllBFSolutions=False):
        self.saveAllBFSolutions = saveAllBFSolutions
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
        self.saveResultsToFile()
    
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
        return np.random.get_state()[1][0]
    
    def setRandomState(self,seed):
        np.random.seed(seed)
    
    def printProgressBar (self,iteration, total, prefix = '', suffix = '', decimals = 1, length = 80, fill = '█', printEnd = "\r"):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + ' ' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        if iteration == total: 
            print()

def simulation(seed,inputFileName,outputFileName,problem,method,crossoverProbability,mutationProbability,numberOfChromosomes,stopConditionType,stopConditionValue,saveAllBFSolutions):
    n1 = Network(inputFileName,outputFileName)
    if seed != 'random':
        n1.setRandomState(seed)
    print('SEED',n1.getRandomState())
    n1.parse()
    if method == 'Brute Force':
        n1.bruteForce(problem,saveAllBFSolutions)
    elif method == 'Evolution':
        n1.evolution(problem,crossoverProbability,mutationProbability,numberOfChromosomes,stopConditionType,stopConditionValue)

if __name__ == "__main__":
    seed = 'random'             # ['random'|(int)]
    inputFileName = 'net4.txt'
    outputFileName = 'result.txt'
    problem = 'DDAP'             # ['DAP'|'DDAP']
    method = 'Brute Force'            # ['Brute Force'|'Evolution']
    crossoverProbability=0.75
    mutationProbability=0.05
    numberOfChromosomes=4
    stopConditionType='generations'# ['time'|'generations'|'mutations'|'bestForN']
    stopConditionValue=5
    saveAllBFSolutions=True
    
    simulation(seed,inputFileName,outputFileName,problem,method,crossoverProbability,mutationProbability,numberOfChromosomes,stopConditionType,stopConditionValue,saveAllBFSolutions)


