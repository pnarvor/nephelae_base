from .types import DataView


class GraphEdge:

    """
    GraphEdge
    
    Simple oriented edge describing the parent/child relationship between two
    DataViews nodes.
    """
    
    def __init__(self, parent, child, edgeId):
        """
        parent and child are DataView types
        """
        self.id     = edgeId
        self.parent = parent
        self.child  = child


    def __str__(self):
        return "DataViewGraph Edge: " + self.id


    def is_connected(self):
        return self.child.has_parent(self.parent)

    
    def disconnect(self):
        if self.is_connected():
            self.child.remove_parent(self.parent)


    def connect(self):
        if not self.is_connected():
            self.child.add_parent(self.parent)

    
    def parent_key(self):
        return self.id.split('__')[0]


    def child_key(self):
        return self.id.split('__')[1]


class GraphNode:

    """
    GraphNode

    Simple graph node describing the set of GraphEdges this node is connected
    to.
    """

    def __init__(self, dataview, parentEdges, childEdges):
        self.data = dataview
        self.parentEdges = parentEdges
        self.childEdges  = childEdges
    
    
class DataViewGraph:

    """
    DataViewGraph

    Manage a set of connected DataViews. Built from the set of DataViews loaded
    from a DataViewsManager.
    """

    def __init__(self, dataviews):
        self.dataviews = dataviews
        self.build_graph()


    def build_graph(self):
        """
        Fill the self.edges and self.nodes attributes by exploring the set of
        dataviews.
        """

        self.edges = {}
        self.nodes = {}
        
        keysList = list(self.dataviews.keys())
        for i, key0 in enumerate(keysList):
            for j, key1 in enumerate(keysList):
                if self.dataviews[key0].has_parent(self.dataviews[key1]):
                    self.new_edge(key1, key0)
                elif self.dataviews[key1].has_parent(self.dataviews[key0]):
                    self.new_edge(key0, key1)


    def new_edge(self, parentKey, childKey):
        newKey = parentKey + '__' + childKey
        if newKey not in self.edges.keys():
            self.edges[newKey] = GraphEdge(self.dataviews[parentKey],
                                           self.dataviews[childKey],
                                           newKey)




