# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 09:35:44 2022

@author: Junqian Li
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json,cgi

highScore = []
input_cgi = ""
class HighScoreTable(BaseHTTPRequestHandler):
    
    def do_GET(self): 
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()

        output = ""
        output += '<html><style type="text/css">'
        output +='.inputZone {width : 50%;}'
        output += '</style><body>'
        output += '<h1>High score table</h1>'
        addedPerson = []
        addedScore = {}
        for record in highScore:
            tmp_name = record['name']
            tmp_score = record['score']
            if tmp_name in addedPerson:
                if addedScore[tmp_name] < tmp_score:
                    highScore.remove({"name":tmp_name,"score":addedScore[tmp_name]})
                    addedScore[tmp_name] = tmp_score
            else:
                addedPerson.append(tmp_name)
                addedScore[tmp_name] = tmp_score
        sortedList = sorted(addedScore.values(),reverse = 1)
        newAddedScore = []
        rank_tmp = 0
        scoreNow_tmp = -1
        for sortedKey in sortedList:
            for key, value in addedScore.items():
                if value==sortedKey:
                    if scoreNow_tmp != value:
                        scoreNow_tmp = value
                        rank_tmp += 1
                    if key in addedPerson:
                        addedPerson.remove(key)
                        newAddedScore.append({"name":key,"score":value,"rank":rank_tmp})
        output += '<br><h2>enter "/get/score/(rank)" to search for player!</h2></br>'
        if '/get/score' in self.path:
            recordsNum = 0
            if len(self.path.split('/')) <= 3:
                index = 0
            elif self.path.split('/')[3] == "":
                index = 0
            else:
                index = int(self.path.split('/')[3])
            for record in newAddedScore:
                if index == 0 or record["rank"] == index:
                    recordsNum += 1
                    output += '<br>'
                    output += '{"rank":%s,"name":%s,"score":%i}'%(record['rank'],record['name'],record['score'])
                    output += '</br>'
            if recordsNum == 0:
                output += '<br><h1>Sorry, no data matches</h1></br>'
            else:
                if index != 0:
                    output += '<br>%i records found for rank %i!</br>'%(recordsNum,index)
                else:
                    output += '<br>%i records found in total!</br>'%(recordsNum)
        elif self.path.endswith('post/score'):
            output += '<h2>Create new record(s)</h2>'
            output += '<form method="POST"  enctype="multipart/form-data" action="/post/score">'
            output += '<br><p><input id="newRecords" name="newRecords" type="text" class="inputZone" placeholder = \'e.g.{"name":"Player1","score":20},{"name":"Player2","score":30}\'>'
            output += '<input type="submit" value="add"></p></br>'
            output += '</form>'
        else:
            output += '<br><h2>View exsiting records by clicking<a href="/get/score"> here</a></h2></br>'
        
        output += '<br><h2>Want to add new records? Click<a href="/post/score"> here</a></h2></br>'

        output += '</body></html>'  
        self.wfile.write(output.encode())

    def do_POST(self):
        print("POST triggered")
        if '/post/score' in self.path :
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            content_len = int(self.headers.get('Content-length'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = content_len
            if ctype == 'multipart/form-data':
                input_cgi = cgi.parse_multipart(self.rfile, pdict)
                input_str = input_cgi.get('newRecords')
            if len(input_cgi) > 0 and input_str[0]!='':
                #input_str = input_cgi["newRecords"].value
                try:
                    input_list_to_json = json.loads("["+input_str[0]+"]")
                    print(input_list_to_json)
                    validNum = 0
                    for postJson in input_list_to_json:
                        tmp_name = postJson["name"]
                        tmp_score = postJson["score"]
                        if tmp_name != None and tmp_score>0:
                            validNum+=1
                            highScore.append({"name":tmp_name,"score":tmp_score})
                except:
                    print("Failed to add record - format error!")
            else:
                print("Failed to add record - the input is empty!")
        else:
            print("Failed to add record - invalid url!")
        self.send_response(301)
        self.send_header('content-type', 'text/html')
        self.send_header('Location', '/get/score')
        self.end_headers()
        
        
def main():
    try:
        port = 8000
        serverAddress = ('localhost',port)
        httpServer = HTTPServer(serverAddress,HighScoreTable)  
        print('Server running on port %s' % port)
        httpServer.serve_forever()
    except KeyboardInterrupt:
        print('Ctrl+C entered. \nThe server interrupted.')
        httpServer.socket.close()

if __name__ == '__main__':
    main()
