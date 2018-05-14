class chunking:
    def __init__(self):
        self.msg=""
        self.size=100
        self.chunk_num=1
    
    def chunks(self,lst, n):
        "Yield successive n-sized chunks from lst"
        for i in xrange(0, len(lst), n):
            yield lst[i:i+n]
    
    

        