from . compile_scripts import compileScript
from .. problems import ExecutionUnitNotSetup
from . code_generator import (getInitialVariables,
                              iterSetupCodeLines,
                              getGlobalizeStatement,
                              iterNodeExecutionLines,
                              linkOutputSocketsToTargets)

class GroupExecutionUnit:
    def __init__(self, network):
        self.network = network
        self.setupScript = ""
        self.setupCodeObject = None
        self.executionData = {}

        self.generateScript()
        self.compileScript()
        self.execute = self.raiseNotSetupException


    def setup(self):
        self.executionData = {}
        exec(self.setupCodeObject, self.executionData, self.executionData)
        self.execute = self.executionData["main"]

    def insertSubprogramFunctions(self, data):
        self.executionData.update(data)

    def finish(self):
        self.executionData.clear()
        self.execute = self.raiseNotSetupException


    def getCodes(self):
        return [self.setupScript]


    def generateScript(self):
        try: nodes = self.network.getSortedAnimationNodes()
        except: return

        variables = getInitialVariables(nodes)
        self.setupScript = "\n".join(self.iterSetupScriptLines(nodes, variables))

    def iterSetupScriptLines(self, nodes, variables):
        yield from iterSetupCodeLines(nodes, variables)
        yield "\n\n"
        yield from self.iterFunctionGenerationScriptLines(nodes, variables)

    def iterFunctionGenerationScriptLines(self, nodes, variables):
        yield self.getFunctionHeader(self.network.groupInputNode, variables)
        yield "    " + getGlobalizeStatement(nodes, variables)
        yield from iterIndented(self.iterExecutionScriptLines(nodes, variables))
        yield "\n"
        yield "    " + self.getReturnStatement(self.network.groupOutputNode, variables)

    def getFunctionHeader(self, inputNode, variables):
        for i, socket in enumerate(inputNode.outputs):
            variables[socket] = "group_input_" + str(i)

        parameterList = ", ".join([variables[socket] for socket in inputNode.sockets[:-1]])
        header = "def main({}):".format(parameterList)
        return header

    def iterExecutionScriptLines(self, nodes, variables):
        yield from linkOutputSocketsToTargets(self.network.groupInputNode, variables)
        for node in nodes:
            if node.bl_idname in ("an_GroupInputNode", "an_GroupOutputNode"): continue
            yield from iterNodeExecutionLines(node, variables)
            yield from linkOutputSocketsToTargets(node, variables)

    def getReturnStatement(self, outputNode, variables):
        if outputNode is None: return "return"
        returnList = ", ".join([variables[socket] for socket in outputNode.inputs[:-1]])
        return "return " + returnList

    def compileScript(self):
        self.setupCodeObject = compileScript(self.setupScript, name = "group: {}".format(repr(self.network.name)))


    def raiseNotSetupException(self):
        raise ExecutionUnitNotSetup()


def iterIndented(lines):
    for line in lines:
        yield "    " + line
