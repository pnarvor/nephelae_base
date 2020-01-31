# from .DataView import DataView

from . import types
from . import DataViewGraph

class DataViewManager:

    """
    DataViewManager

    Helper class to build and manage DataViews.

    Load DataViews graph from the parsed yaml configuration, maintain a fixed
    graph of connections between dataviews, and can freely connect or
    disconnect them.

    """

    def from_yaml_config(config, database=None):
        
        manager = DataViewManager()
        manager.load_yaml_config(config, database)
        return manager


    def __init__(self, dataviews={}, displayedViews=[], database=None):
        self.dataviews      = dataviews
        self.displayedViews = displayedViews
        self.database       = database
        self.update_dataview_graph()
        

    def keys(self):
        return self.dataviews.keys()


    def __getitem__(self, key):
        return self.dataviews[key]


    def load_yaml_config(self, config, database=None):
        self.database = database
        for key in config:
            self.load_data_view(key, config)
        self.update_dataview_graph()


    def load_data_view(self, key, config):
        """
        Load a single view (can trigger nloading of parent views).
        """

        if key == 'displayable':
            if isinstance(config[key], str):
                self.displayedViews = [config[key]]
            else:
                self.displayedViews = config[key]
            return

        # Ignore if already loaded.
        if key in self.dataviews.keys():
            return
        
        # Load parents of current view (before curren view)>
        if 'parents' in config[key]:
            for parentId in config[key]['parents']:
                self.load_data_view(parentId, config)
        
        # Load current view.
        if config[key]['type'] == 'DataView':
            self.dataviews[key] = types.DataView(config[key]['name'],
                parents=[self.dataviews[parentId]
                         for parentId in config[key]['parents']])
        elif config[key]['type'] == 'DatabaseView':
            self.dataviews[key] = types.DatabaseView(config[key]['name'], 
                    self.database, config[key]['tags'])
        elif config[key]['type'] == 'TimeView':
            self.dataviews[key] = types.TimeView(config[key]['name'],
                parents=[self.dataviews[parentId]
                         for parentId in config[key]['parents']])
        elif config[key]['type'] == 'Function':
            self.dataviews[key] = types.Function(config[key]['name'],
                parents=[self.dataviews[parentId]
                         for parentId in config[key]['parents']])
        elif config[key]['type'] == 'Scaling':
            if 'gain' in config[key].keys():
                gain = config[key]['gain']
            else:
                gain = 1.0
            if 'offset' in config[key].keys():
                offset = config[key]['offset']
            else:
                offset = 0.0
            self.dataviews[key] = types.Scaling(config[key]['name'],
                gain=float(gain), offset=float(offset),
                parents=[self.dataviews[parentId]
                         for parentId in config[key]['parents']])
        elif config[key]['type'] == 'HumidityCalibration':
            try:
                lt = config[key]['lt']
                gain_1 = config[key]['gain_1']
                gain_2 = config[key]['gain_2']
                offset_1 = config[key]['offset_1']
                offset_2 = config[key]['offset_2']
            except KeyError as e:
                print('Data missing for the creation of HumidityCalibration')
                raise e
            self.dataviews[key] = types.HumidityCalibration(config[key]['name'],
                lt=float(lt),
                gain_1=float(gain_1), offset_1=float(offset_1),
                gain_2=float(gain_2), offset_2=float(offset_2),
                parents=[self.dataviews[parentId] 
                    for parentId in config[key]['parents']]
            )
        elif config[key]['type'] == 'CloudSensorProcessing':
            try:
                cloudTags    = config[key]['cloud_tags']
                energyTags   = config[key]['energy_tags']
                alpha        = float(config[key]['alpha'])
                beta         = float(config[key]['beta'])
                scaling      = float(config[key]['scaling'])
                lengthMedian = int(config[key]['lengthMedian'])
            except KeyError as e:
                print('Data missing for the creation of CloudSensorProcessing')
                raise e
            self.dataviews[key] = types.CloudSensorProcessing(
                name=config[key]['name'], database=self.database,
                searchTagsCloud=cloudTags,
                searchTagsEnergy=energyTags,
                alpha=alpha, beta=beta, scaling=scaling,
                lengthMedian=lengthMedian
            )
        else:
            raise KeyError("Unknown data_view type")


    def update_dataview_graph(self):
        if len(self.dataviews) > 0:
            self.viewGraph = DataViewGraph(self.dataviews)



