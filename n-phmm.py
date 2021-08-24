import enum
import json
match_states = list()
deletion_states = list()
insertion_states = list()
beginning_end_states=list()
data = list()
class stateType(enum.Enum):
    Beginning = 0
    Match = 1
    Insertion = 2
    Deletion = 3
    Unstable = 4
    Ending = 5

class State:

    def __init__(self, name, type, row, probabilities):
        self.name = name
        self.type = type
        self.row = row
        self.probabilities = probabilities

def readFile(filename):
    with open(filename, "r")as file:
        for _hold in file:
            _hold = _hold.replace(",", "")
            _hold = _hold.replace("\n", "")
            data.append(_hold)
    return data

def isMatch(state):
    return state.type == stateType.Match


def isBeginning(state):
    return state.type == stateType.Beginning


def isNucleo(element):
    return element == "A" or element == "T" or element == "C" or element == "G"

def get_index(data, index):
    row = list()
    ind = 0
    for _hold in data:
        if _hold[index] == "_":
            x = "s" + str(ind + 1)
            row.append(x)
        ind += 1
    return row

def get_unstable_array(data):
    unstable_indexes = []
    unstable_array = []
    count = 0
    for _hold in range(len(data[0])):
        for j in data:
            if j[_hold] == '_':
                count += 1
        if count > 2:
            unstable_indexes.append(_hold)
        unstable_array.append(count)
        count = 0
    return unstable_indexes, unstable_array

def createModel(data, unstable_indexes):
    match_count = 0
    deletion_count = 1
    insertion_count = 0
    
    s=[]
    init = [0,0,0]
    #creating begining
    for i in range(len(data)):
        s.append("S{}".format(i+1))
    new_state = State("b",stateType.Beginning,s,init)
    match_count += 1
    beginning_end_states.append(new_state)
    s=[]
    init = [0,0,0]
    new_state = State("i{}".format(insertion_count),stateType.Insertion,s,init)
    insertion_count += 1
    insertion_states.append(new_state)
    #creating ending
    s=[]
    init = [0,0,0]
    for i in range(len(data)):
        s.append("S{}".format(i+1))
    new_state = State("e",stateType.Ending,s, init)
    new_state.probabilities_count=1
    beginning_end_states.append(new_state)
    for index in range(len(data[0])):     
        #creating match ,insertion ,deletion
        if(not(index in unstable_indexes)):
            s=[]
            init = [0,0,0]
            new_state = State("m{}".format(match_count),
                              stateType.Match,s,init)
            match_count += 1
            match_states.append(new_state)
            s=[]
            init = [0,0,0]
            new_state = State("i{}".format(insertion_count),stateType.Insertion,s,init)
            insertion_count += 1
            insertion_states.append(new_state)
            s=[]
            init = [0,0,0]
            new_state = State("d{}".format(deletion_count),stateType.Deletion,s,init)
            deletion_count += 1
            deletion_states.append(new_state)
                
    return match_states,insertion_states,deletion_states,beginning_end_states

def calculationManager(data):
    
    unstable=get_unstable_array(data)
    index=1
    mapping=list()
    #assign states
    for i in data:
        row=list()
        step=0
        for j in range(len(data[0])):
            if(j in unstable[0]):
                if(isNucleo(i[j])): 
                    insertion_states[step].row.append("S{}".format(index))
                    x=insertion_states[step].name
                    row.append(x)
                else:
                    pass
            else:
                if(isNucleo(i[j])):
                    match_states[step].row.append("S{}".format(index))
                    x=match_states[step].name
                    row.append(x)
                    step+=1
                else:
                    deletion_states[step].row.append("S{}".format(index))
                    x=deletion_states[step].name
                    row.append(x)
                    step+=1
        mapping.append(row)            
        index+=1
    
    for i in mapping:
        print(i)
    
    #calculating beginning states
    for i in range(len(data)):
        if(("S{}".format(i+1) in match_states[0].row) and not("S{}".format(i+1) in insertion_states[0].row)):
            beginning_end_states[0].probabilities[0]+=1
        elif(("S{}".format(i+1) in match_states[0].row) and ("S{}".format(i+1) in insertion_states[0].row)):
            beginning_end_states[0].probabilities[1]+=1
        else:
            beginning_end_states[0].probabilities[2]+=1
    beginning_end_states[0].probabilities[0]/=len(beginning_end_states[0].row)
    beginning_end_states[0].probabilities[1]/=len(beginning_end_states[0].row)
    beginning_end_states[0].probabilities[2]/=len(beginning_end_states[0].row)
    #calculating match states
    for i in range(len(match_states)):
        if(i==len(match_states)-1):
            for j in range(len(match_states[i].row)):
                if((match_states[i].row[j] in beginning_end_states[1].row) and not(match_states[i].row[j] in insertion_states[i+1].row)):
                    match_states[i].probabilities[0]+=1
                elif((match_states[i].row[j] in beginning_end_states[1].row) and (match_states[i].row[j] in insertion_states[i+1].row)):
                    match_states[i].probabilities[1]+=1
                else:
                    match_states[i].probabilities[2]+=1
        else:
            for j in range(len(match_states[i].row)):
                if((match_states[i].row[j] in match_states[i+1].row) and not(match_states[i].row[j] in insertion_states[i+1].row)):
                    match_states[i].probabilities[0]+=1
                elif((match_states[i].row[j] in match_states[i+1].row) and (match_states[i].row[j] in insertion_states[i+1].row)):
                    match_states[i].probabilities[1]+=1
                else:
                    match_states[i].probabilities[2]+=1
    
    for j in range(len(match_states)):
        try:
            match_states[j].probabilities[0]/=len(match_states[j].row)
            match_states[j].probabilities[1]/=len(match_states[j].row)
            match_states[j].probabilities[2]/=len(match_states[j].row)
        except:
            pass

    #calculating insertion states
    for i in range(len(insertion_states)):
        pas=[]
        if(i==len(insertion_states)-1):
            for j in range(len(insertion_states[i].row)):
                if(insertion_states[i].row[j] in pas):
                    continue
                if((insertion_states[i].row[j] in beginning_end_states[1].row) and (insertion_states[i].row.count(insertion_states[i].row[j])<=1)):
                    insertion_states[i].probabilities[0]+=1
                elif((insertion_states[i].row[j] in beginning_end_states[1].row) and (insertion_states[i].row.count(insertion_states[i].row[j])>1)):
                    pas.append(insertion_states[i].row[j])
                    insertion_states[i].probabilities[0]+=1
                    insertion_states[i].probabilities[1]+=(insertion_states[i].row.count(insertion_states[i].row[j])-1)
                elif((insertion_states[i].row[j] in beginning_end_states[1].row) and (insertion_states[i].row.count(insertion_states[i].row[j])<=1)):
                    insertion_states[i].probabilities[2]+=1
                else:
                    pas.append(insertion_states[i].row[j])
                    insertion_states[i].probabilities[2]+=1
                    insertion_states[i].probabilities[1]+=(insertion_states[i].row.count(insertion_states[i].row[j])-1)
        else:
            for j in range(len(insertion_states[i].row)):
                if(insertion_states[i].row[j] in pas):
                    continue
                if((insertion_states[i].row[j] in match_states[i].row) and (insertion_states[i].row.count(insertion_states[i].row[j])<=1)):
                    insertion_states[i].probabilities[0]+=1
                elif((insertion_states[i].row[j] in match_states[i].row) and (insertion_states[i].row.count(insertion_states[i].row[j])>1)):
                    pas.append(insertion_states[i].row[j])
                    insertion_states[i].probabilities[0]+=1
                    insertion_states[i].probabilities[1]+=(insertion_states[i].row.count(insertion_states[i].row[j])-1)
                elif((insertion_states[i].row[j] in deletion_states[i].row) and (insertion_states[i].row.count(insertion_states[i].row[j])<=1)):
                    insertion_states[i].probabilities[2]+=1
                else:
                    pas.append(insertion_states[i].row[j])
                    insertion_states[i].probabilities[2]+=1
                    insertion_states[i].probabilities[1]+=(insertion_states[i].row.count(insertion_states[i].row[j])-1)

    for j in range(len(insertion_states)):
        try:
            insertion_states[j].probabilities[0]/=len(insertion_states[j].row)
            insertion_states[j].probabilities[1]/=len(insertion_states[j].row)
            insertion_states[j].probabilities[2]/=len(insertion_states[j].row)
        except:
            pass
        
    #calculating deletion states
    for i in range(len(deletion_states)):
        if(i==len(deletion_states)-1):
            pass
        else:
            for j in range(len(deletion_states[i].row)):
                if((deletion_states[i].row[j] in deletion_states[i+1].row) and not(deletion_states[i].row[j] in insertion_states[i+1].row)):
                    deletion_states[i].probabilities[2]+=1
                elif((deletion_states[i].row[j] in deletion_states[i+1].row) and (deletion_states[i].row[j] in insertion_states[i+1].row)):
                    deletion_states[i].probabilities[1]+=1
                else:
                    deletion_states[i].probabilities[0]+=1
    
    for j in range(len(deletion_states)):
        try:
            deletion_states[j].probabilities[0]/=len(deletion_states[j].row)
            deletion_states[j].probabilities[1]/=len(deletion_states[j].row)
            deletion_states[j].probabilities[2]/=len(deletion_states[j].row)
        except:
            pass

                
#writting json file              
def write_file():
    datas = {}
    datas['states']= []
    datas['states'].append({'state':{
        'name': str(beginning_end_states[0].name),
        'type': str(beginning_end_states[0].type.name),
        'match-probability': str(beginning_end_states[0].probabilities[0]),
        'deletion-probability': str(beginning_end_states[0].probabilities[2]),
        'insertion-probabilty': str(beginning_end_states[0].probabilities[1]), 
        }})
    
    if(insertion_states[0].probabilities[0]!=0 or insertion_states[0].probabilities[1]!=0 or insertion_states[0].probabilities[2]!=0 ):
        datas['states'].append({'state':{
        'name': str(insertion_states[0].name),
        'type': str(insertion_states[0].type.name),
        'match-probability': str(insertion_states[0].probabilities[0]),
        'deletion-probability': str(insertion_states[0].probabilities[2]),
        'insertion-probabilty': str(insertion_states[0].probabilities[1]), 
        }})
  
    for i in range(len(match_states)):
        datas['states'].append({'state':{
        'name': str(match_states[i].name),
        'type': str(match_states[i].type.name),
        'match-probability': str(match_states[i].probabilities[0]),
        'deletion-probability': str(match_states[i].probabilities[2]),
        'insertion-probabilty': str(match_states[i].probabilities[1]), 
        }})
        
        if(insertion_states[i+1].probabilities[0]!=0 or insertion_states[i+1].probabilities[1]!=0 or insertion_states[i+1].probabilities[2]!=0):
            datas['states'].append({'state':{
            'name': str(insertion_states[i+1].name),
            'type': str(insertion_states[i+1].type.name),
            'match-probability': str(insertion_states[i+1].probabilities[0]),
            'deletion-probability': str(insertion_states[i+1].probabilities[2]),
            'insertion-probabilty': str(insertion_states[i+1].probabilities[1]), 
            }})
        
        if(deletion_states[i].probabilities[0]!=0 or deletion_states[i].probabilities[1]!=0 or deletion_states[i].probabilities[2]!=0):
            datas['states'].append({'state':{
            'name': str(deletion_states[i].name),
            'type': str(deletion_states[i].type.name),
            'match-probability': str(deletion_states[i].probabilities[0]),
            'deletion-probability': str(deletion_states[i].probabilities[2]),
            'insertion-probabilty': str(deletion_states[i].probabilities[1]), 
            }})

    datas['states'].append({'state':{
        'name': str(beginning_end_states[1].name),
        'type': str(beginning_end_states[1].type.name),
        'match-probability': str(beginning_end_states[1].probabilities[0]),
        'deletion-probability': str(beginning_end_states[1].probabilities[2]),
        'insertion-probabilty': str(beginning_end_states[1].probabilities[1]), 
        }})
          
    with open("output.json","w") as wr:
        json.dump(datas,wr,indent=2)

if __name__ == "__main__":
    data = readFile("data.txt")

    unstable_indexes, unstable_array = get_unstable_array(data)
    model = createModel(data, unstable_indexes)
    
    calculationManager(data)
    
    for state in model[0]:
        print(state.name, state.type.name, state.row,state.probabilities)
    
    write_file()
    
