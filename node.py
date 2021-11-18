from flask import Flask, jsonify, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
#since the data type has 3 definitive levles, i have initiated 3 levels of nodes

#define class for root node P1
class NodeP1():
    def __init__(self, WebReq, TimeSpent):
        self.WebReq = WebReq
        self.TimeSpent = TimeSpent
        self.children = []
    def add_child(self, obj):
        self.children.append(obj)

#define class for parent node P2
class NodeP2(NodeP1):
    def __init__(self, WebReq, TimeSpent, Country):
        super().__init__(WebReq,TimeSpent)
        self.Country = Country

#define class for child node C1
class NodeC1(NodeP1):
    def __init__(self, WebReq, TimeSpent, Device):
        super().__init__(WebReq, TimeSpent)
        self.Device = Device

#Initialize root node and set values to zero
Root_Node = NodeP1(0,0)


#Define tree class with methods to add, search and update node values
class Tree():
    def __init__(self,root):
        self.root = root

    def add_node(self,node):
        self.root.add_child(node)

    #searches nodes based on country name in the p1 level of nodes
    def search_p1Node(self,country):
        foundp1 = False

        for c in self.root.children:
            if c.Country == country:
                foundp1 = c
                break
        return foundp1

    # searches nodes based on device name in the c1 level of nodes
    def search_c1Node(self,device,node):
        foundc1 = False
        for c1 in node.children:
            if c1.Device == device:
                foundc1 = c1
                break
        return foundc1

    #updates the value of node if found, else, creates a node
    def update_node(self,country,device,webreq,timespent):
        self.root.WebReq += webreq
        self.root.TimeSpent += timespent
        foundp1 = self.search_p1Node(country)

        if foundp1!=False:
            foundc1 = self.search_c1Node(device,foundp1)
            foundp1.WebReq+=webreq
            foundp1.TimeSpent+=timespent
            if foundc1!=False:
                foundc1.WebReq += webreq
                foundc1.TimeSpent += timespent
            if foundc1==False:
                node_temp = NodeC1(webreq,timespent,device)
                foundp1.add_child(node_temp)
        elif foundp1==False:
            temp_node = NodeP2(webreq,timespent,country)
            temp_node.add_child(NodeC1(webreq,timespent,device))
            self.add_node(temp_node)

#root node set in Tree
tree_db = Tree(root=Root_Node)

tree_db.update_node('US','Tablet',30,50)
tree_db.update_node('IN','Mobile',70,30)
tree_db.update_node('US','Tablet',10,60)
tree_db.update_node('US','Mobile',20,40)


#class for the /insert URI
class InsertVals(Resource):
    def post(self):
        try:
            data = request.get_json()
            vals = {'country':None,'device':None,'webreq':None,'timespent': None}
            for d in data['dim']:
                vals[d['key']]=d['val']
            for d in data['metrics']:
                vals[d['key']]=d['val']
            tree_db.update_node(vals['country'],vals['device'],vals['webreq'],vals['timespent'])
            return 201
        except:
            return jsonify("invalid json format")


#class for the /query URI
class Query(Resource):
    def post(self):
        try:
            data = request.get_json()
            country = data['dim'][0].get('val')
            out = tree_db.search_p1Node(country)
            if out==False:
                return jsonify("Country not found")
            if len(data['dim'])>1:
                device = data['dim'][1].get('val')
                out = tree_db.search_c1Node(device,out)
                if out == False:
                    return jsonify("Device not found")
                return jsonify({
                    "dim": [{"key": "device", "val": out.Device}],
                    "metrics": [{"key": "webreq", "val": out.WebReq}, {"key": "timespent", "val": out.TimeSpent}]
                })

            return jsonify({
                "dim": [{"key": "country","val": out.Country}],
                "metrics": [{"key": "webreq","val": out.WebReq},{"key": "timespent","val": out.TimeSpent}]
            })
        except:
            return jsonify('Invalid json format')



api.add_resource(InsertVals, '/insert')
api.add_resource(Query, '/query')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
