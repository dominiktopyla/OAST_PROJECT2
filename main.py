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
        self.demandVolume = int(parameters[2])
        self.numberOfPaths = int(lines[1])
        self.paths = []
        paths = lines[2:self.numberOfPaths+2]
        for path in paths:
            self.paths.append(Path(path))        
    def __str__(self):
        message = '[ŻĄDANIE]: '+str(self.startNode)+'--'+str(self.endNode)+'\n\tzapotrzebowanie='+str(self.demandVolume)+'\n'
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






if __name__ == "__main__":
    n1 = Network()
    n1.parse('input/net12_1.txt')
    n1.show()