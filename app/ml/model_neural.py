import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        
        self.l1 = nn.Linear(input_size, hidden_size)  
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        self.l3 = nn.Linear(hidden_size, num_classes) 

        self.relu = nn.ReLU() 
        self.leaky_relu = nn.LeakyReLU(negative_slope=0.01) 
        self.dropout = nn.Dropout(0.5) 
        self.batch_norm1 = nn.BatchNorm1d(hidden_size) 
        self.batch_norm2 = nn.BatchNorm1d(hidden_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):

        out = self.l1(x)
        out = self.relu(out)  
        out = self.batch_norm1(out)
        out = self.dropout(out) 
        
        out = self.l2(out)
        out = self.relu(out)
        out = self.batch_norm2(out) 
        out = self.dropout(out) 
        
        out = self.l3(out)
        out = self.softmax(out)
        
        return out
