#Author-Greg Vialle 2018
#Version 1.0
#License GPL

#Description-Creates an epicyclic helical rotor and stator. The rotor will 
#typically need a shaft added. The stator generated is actually the solid model 
#of the stator cavity. As the stator is frequently molded out of silicone, this 
#allows the user to use the generated model for creating the mold tool, as well 
#as more latitude in creating the external stator geometry (from which the 
#generated stator body can be cut via a boolean operation).

#Credits:
    #Explanations of Moineau Operation:
        #http://www2.mat.dtu.dk/people/J.Gravesen/MoineauPump/

    #Explanations of cycloid geometry:
        #http://en.wikipedia.org/wiki/Hypocycloid
        #http://en.wikipedia.org/wiki/Epicycloid
#Notes:
    # Does not currently do ANY sanity checking for input values; use at your own risk

    # AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
    # DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
    # AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
    # UNINTERRUPTED OR ERROR FREE.

import adsk.core, adsk.fusion, traceback
import math

defaultPartName = "Stator"
defaultLobes = 3
defaultMajorDiameter = 12.
defaultMinorDiameter = 6.
defaultTurns = 2.
defaultHeight = 30.
defaultPosition = (0., 0., 0., math.pi/6)

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

newComp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

class MoineauCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            stator = Part()
            stator.partName = "Stator"
            for input in inputs:
                if input.id == 'lobes':
                    stator.lobes = input.value
                elif input.id == 'majorDiameter':
                    stator.majorDiameter = unitsMgr.evaluateExpression(input.expression, "mm")
                elif input.id == 'turns':
                    stator.turns = input.value
                elif input.id == 'height':
                    stator.height = unitsMgr.evaluateExpression(input.expression, "mm")
                stator.position =  (0, 0, 0, math.pi / stator.lobes / 2.)

            stator.build()
            args.isValidResult = True

            rotor = Part()
            rotor.partName = "Rotor"
            rotor.lobes = stator.lobes - 1
            rotor.turns = stator.lobes * stator.turns / rotor.lobes
            rotor.majorDiameter = (stator.majorDiameter + stator.minorDiameter) / 2.
            rotor.height = stator.height
            rotor.position = (0., (stator.majorDiameter - rotor.majorDiameter) / 2., 0., math.pi / rotor.lobes / 2.)
            rotor.build()

            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
#%%
class MoineauCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
#%%
class MoineauCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = MoineauCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = MoineauCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = MoineauCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs

            #display diagram and instructions
            mainImage = inputs.addImageCommandInput('moineauImage', '', './Moineau.png')
            
            # Create Instructions group 
            groupInstructions = inputs.addGroupCommandInput('group1', 'Instructions')
            groupInstructions.isExpanded = False
            instructionsTextString = str('Creates an epicyclic helical rotor and stator (i.e., Moineau pump). ') 
            instructionsTextString += str('The rotor will need a shaft added, consistent with your drive design. ')
            instructionsTextString += str('The stator generated is actually the solid model of the stator cavity. ')
            instructionsTextString += str('Since the stator is typically molded out of silicone, ' )
            instructionsTextString += str('this allows the user to use the generated model both for creating the mold tool, ')
            instructionsTextString += str('and for creating the external stator geometry ')
            instructionsTextString += str('(from which the generated stator body can be cut via a boolean operation).')
                
            instructionsText = groupInstructions.children.addTextBoxCommandInput('instructions', '', instructionsTextString, 12, True)

            #user entered parameters
            groupEntries = inputs.addGroupCommandInput('group2', 'Entered Parameters')
            groupEntries.isExpanded = True     
           
            initLobes = adsk.core.ValueInput.createByReal(defaultLobes)
            lobeEntry = groupEntries.children.addIntegerSpinnerCommandInput('lobes', 'Stator Lobes', 2, 10, 1, defaultLobes)
            lobeEntry.tooltip = "At least 2, values greater than 10 may crash Fusion360"

            initMajorDiameter = adsk.core.ValueInput.createByReal(defaultMajorDiameter)
            majDEntry = groupEntries.children.addValueInput('majorDiameter', 'Stator Major Diameter','mm',initMajorDiameter)
            majDEntry.tooltip = "Controls the in plane size."

            initTurns = adsk.core.ValueInput.createByReal(defaultTurns)
            TEntry = groupEntries.children.addValueInput('turns', 'Turns', '', initTurns)
            TEntry.tooltip = "Use negative values for LH pitch angle"

            initHeight = adsk.core.ValueInput.createByReal(defaultHeight)
            HEntry = groupEntries.children.addValueInput('height', 'Pump Height', 'mm', initHeight)
            HEntry.tooltip = "Adjust with lobes and turns to give the desired pitch angle"

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
#%%
class Part:
    def __init__(self):
        self._partName = defaultPartName
        self._lobes = defaultLobes
        self._majorDiameter = defaultMajorDiameter
        self._minorDiameter = defaultMinorDiameter
        self._height = defaultHeight
        self._turns = defaultTurns
        self._position = defaultPosition

    #properties
    @property
    def partName(self):
        return self._partName
    @partName.setter
    def partName(self, value):
        self._partName = value

    @property
    def majorDiameter(self):
        return self._majorDiameter
    @majorDiameter.setter
    def majorDiameter(self, value):
        self._majorDiameter = value

    @property
    def minorDiameter(self):
        self._minorDiameter = self.majorDiameter * (self.lobes - 1) / (self.lobes + 1)
        return self._minorDiameter

    @property
    def lobes(self):
        return self._lobes
    @lobes.setter
    def lobes(self, value):
        self._lobes = value

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, value):
        self._height = value

    @property
    def position(self):
        return self._position
    @position.setter
    def position(self, value):
        self._position = value

    @property
    def turns(self):
        return self._turns
    @turns.setter
    def turns(self, value):
        self._turns = value


    @property
    def isValid(self):
        valid = self.lobes > 1
        valid &= self.majorDiameter > 0
        valid &= self.height > self.majorDiameter
        valid &= math.modulus(self.turns / int(self.turns)) == 0
        valid &= math.modulus(self.lobes / int(self.lobes)) == 0
        return valid


    def build(self):
        global newComp
        newComp = createNewComponent()
        newComp.name = self.partName
        
        if newComp is None:
            ui.messageBox('New component failed to create', 'New Component Failed')
            return

        #Set up cycloidal geometric parameters 
        steps = 50
        Ravg = (self.majorDiameter + self.minorDiameter) / 4.
        Rcyc = (2. * Ravg - self.minorDiameter) / 4.
        q = 2 * math.pi / float(steps)
        sweepAngle = self.turns * 360

        # Create a new sketch.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        xzPlane = newComp.xZConstructionPlane

        # Create path
        sketchVertical = sketches.add(xzPlane)
        sketchLines = sketchVertical.sketchCurves.sketchLines
        startPt = adsk.core.Point3D.create(self.position[0], self.position[2], self.position[1])
        endPt = adsk.core.Point3D.create(self.position[0], self.position[2] - self.height, self.position[1])
        line1 = sketchLines.addByTwoPoints(startPt, endPt)
        path = newComp.features.createPath(line1)

        #Create point collection
        points = adsk.core.ObjectCollection.create()

        sketch = sketches.add(xyPlane)

        # Generate curve points
        for i in range(0, steps):
            t = i * q

            if math.sin(Ravg * t / (Rcyc * 2)) > 0:
                R = Rcyc
            else:
                R = -Rcyc

            B = Ravg - R
            x = B * math.cos(t) + R * math.cos((B / R) * t)
            y = B * math.sin(t) - R * math.sin((B / R) * t)
            r = math.sqrt(x ** 2 + y ** 2)
            theta = math.atan2(x, y)
            x1 = r * math.cos(theta - self.position[3]) + self.position[0]
            y1 = r * math.sin(theta - self.position[3]) + self.position[1]
            points.add(adsk.core.Point3D.create(x1, y1, 0))
            if i == 0:
                x0 = x1
                y0 = y1
        # Close curve
        points.add(adsk.core.Point3D.create(x0, y0, 0))

        # Create spline section and profile
        sketch.sketchCurves.sketchFittedSplines.add(points)
        profile = sketch.profiles[0]

        # Sweep
        sweeps = newComp.features.sweepFeatures
        newSweep = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        sweepInput = sweeps.createInput(profile, path, newSweep)
        sweepInput.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        sweepInput.taperAngle = adsk.core.ValueInput.createByString('0 deg')
        sweepInput.twistAngle = adsk.core.ValueInput.createByString(str(sweepAngle) + ' deg')
        sweep = sweeps.add(sweepInput)
#%%

def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('Rotor')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Rotor',
                    'Create Moineau',
                    'Create a moineau pump.',
                    './') # relative resource file path is specified

        onCommandCreated = MoineauCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
