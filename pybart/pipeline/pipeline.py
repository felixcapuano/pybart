
class Pipeline:
    """Default pipeline to overwrite"""
    
    def __init__(self, parent):
        print('This is the default pipeline.')
    
    def new_epochs(self, label, epochs):
        print('Capturing epoch `{}` with shape : {}'. format(label, epochs.shape))
    
    def setting(self):
        print('No setting to show!')
        
    def reset(self):
        print('Reset the pipeline')