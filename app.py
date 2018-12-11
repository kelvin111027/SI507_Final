from flask import Flask, render_template, request, redirect
import model

app = Flask(__name__)
state_chosen = ''
park_chosen = ''
instate_data = []
lodge_lst = []

@app.route("/")
def index():
    ##print the home page
    return render_template("index.html", state_lst=list(model.final.state_dict.values()))

@app.route("/states", methods=['GET','POST'])
def states():
    ##print the states table
    if request.method == 'POST':
        sortby = request.form['sortby']
        sortorder = request.form['sortorder']
        sorted_states = model.sort_states(sortby, sortorder)
    else:
        sorted_states = model.sort_states()
    return render_template("states.html", states=sorted_states)

@app.route("/instate", methods=['GET','POST'])
def instate():
    #print the table of one state
    global state_chosen
    global instate_data
    if request.method == 'POST':
        state_chosen = request.form['state_chosen']
        instate_data = model.get_instate(state_chosen)
    return render_template("instate.html", state_name=state_chosen, instate=instate_data)

@app.route("/lodge", methods=['GET','POST'])
def lodge():
    #print the table of lodge of one park
    global park_chosen
    global lodge_lst
    if request.method == 'POST':
        park_chosen = request.form['park_chosen']
        lodge_lst = model.get_hotel(park_chosen)
    return render_template("lodge.html", park_name=park_chosen, hotels=lodge_lst)

@app.route("/statemap", methods=["POST"])
def plot_park_instate():
    #execute the plot
    stateForMap = request.form['statemap']
    model.statemap(stateForMap)
    return redirect("/instate")

@app.route("/lodgemap", methods=["POST"])
def plot_lodge_nearby():
    #execute the plot
    parkForMap = request.form['lodgemap']
    model.lodgemap(parkForMap)
    return redirect("/lodge")

@app.route("/graph")
def graph():
    #show the graph
    model.rcRanking()
    return redirect("/")

@app.route("/piechart")
def pie():
    #show the pie chart
    model.pieChart()
    return redirect("/")

if __name__=="__main__":
    model.init_states()
    app.run(debug=True)
