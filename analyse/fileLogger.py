
# Create a custom logger class
class FileLogger():
    def __init__(self, name, filename=f'tmp.log'):
        self.filename = filename
    
    def finfo(self, msg, flush=True, end=True):
        with open(self.filename, "a") as myfile:
            myfile.write(str(msg) + "\n")
            
            # x = len(myfile.readlines())
            # if x > 2000:
                
            myfile.close()
        
