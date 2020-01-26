class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def addEdge(self,u,v,w):
        self.graph.append([u,v,w])

    def printDistance(self, distance):
        print("vertex distance from given node")
        for i in range(self.V):
            print("%d \t\t %d" %(i, distance[i]))

    def BellmanFordDistance(self, source):
        distance = [self.V]
        for i in range (self.V):
            distance.append(float("Inf"))
        distance[source] = 0
        for j in range(self.V - 1):
            for u, v, w in self.graph:
                if distance[u] != float("Inf") and distance[u]+w < distance[v]:
                    distance[v] = distance[u]+w

        for u, v, w in self.graph:
            if distance[u] != float("Inf") and distance[u] + w < distance[v]:
                print("Graph contains negative weight cycle")
        return self.printDistance(distance)

g = Graph(5)
g.addEdge(0, 1, -1)
g.addEdge(0, 2, 4)
g.addEdge(1, 2, 3)
g.addEdge(1, 3, 2)
g.addEdge(1, 4, 2)
g.addEdge(3, 2, 5)
g.addEdge(3, 1, 1)
g.addEdge(4, 3, -3)

g.BellmanFordDistance(0)

