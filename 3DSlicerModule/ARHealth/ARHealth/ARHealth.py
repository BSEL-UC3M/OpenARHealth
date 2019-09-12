import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import math

#
# ARHealth
#
class ARHealth(ScriptedLoadableModule):
 
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "AR Health: Model Position" 
    self.parent.categories = ["ARHealth"]
    self.parent.dependencies = []
    self.parent.contributors = ["Rafael Moreta (UC3M), David Garcia (UC3M)"] 
    self.parent.helpText = """
    ARHealth is a module that enables the positioning of any 3D model over a marker for an AR application.
    """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
    This module was developed by Rafael Moreta-Martinez and David Garcia-Mato
    """ 

#
# ARHealthWidget
#
class ARHealthWidget(ScriptedLoadableModuleWidget):

  def setup(self):

    ScriptedLoadableModuleWidget.setup(self)

    self.logic = ARHealthLogic()

    # Layout setup
    self.layoutManager = slicer.app.layoutManager()
    self.setCustomLayout()
    self.layoutManager.setLayout(self.customLayout_1_ID) # Set 3D only view layout

    #-------------------------------------------------------#
    #------------------- Load Models -----------------------#
    #-------------------------------------------------------#
    
    # Creacion layout
    self.collapsibleButtonInit = ctk.ctkCollapsibleButton()
    self.collapsibleButtonInit.text = "INITIALIZATION"
    self.collapsibleButtonInit.collapsed = False
    self.layout.addWidget(self.collapsibleButtonInit)
    formLayout_init = qt.QFormLayout(self.collapsibleButtonInit)

    # Reset button
    self.resetButton = qt.QPushButton("RESET")
    self.resetButton.toolTip = "Reset scene."
    self.resetButton.enabled = True
    formLayout_init.addRow(self.resetButton) 

    # Mode selection
    self.modeSelection_GroupBox = ctk.ctkCollapsibleGroupBox()
    self.modeSelection_GroupBox.setTitle("Mode")
    self.modeSelection_GroupBox.enabled = True
    formLayout_init.addRow(self.modeSelection_GroupBox)
    modeSelection_GroupBox_Layout = qt.QFormLayout(self.modeSelection_GroupBox)
    modeSelection_H_Layout = qt.QHBoxLayout()
    modeSelection_GroupBox_Layout.addRow(modeSelection_H_Layout)

    ## Reference radio button
    self.mode1_radioButton = qt.QRadioButton('Visualization')
    self.mode1_radioButton.checked = True
    modeSelection_H_Layout.addWidget(self.mode1_radioButton)

    ## No Reference radio button
    self.mode2_radioButton = qt.QRadioButton('Registration')
    modeSelection_H_Layout.addWidget(self.mode2_radioButton)

    # Button Load Marker Model
    self.loadMarkerButton = qt.QPushButton("Load Marker Model")
    self.loadMarkerButton.toolTip = "Load Marker Model"
    self.loadMarkerButton.enabled = True
    formLayout_init.addRow(self.loadMarkerButton) 

    """
    # Text to load model
    self.inputModel_label = qt.QLabel("Model Path: ")
    self.inputModel_textInput = qt.QLineEdit()
    self.inputModel_textInput.text = ""
    formLayout_init.addRow(self.inputModel_label, self.inputModel_textInput)
    """
    ## Load Models
    self.LoadModelsGroupBox = ctk.ctkCollapsibleGroupBox()
    self.LoadModelsGroupBox.setTitle("Load Models")
    formLayout_init.addRow(self.LoadModelsGroupBox)
    LoadModelsGroupBox_Layout = qt.QFormLayout(self.LoadModelsGroupBox)

    # Data Stream File Path Selector
    self.modelsPathEdit = ctk.ctkPathLineEdit()
    self.modelsPathEdit.enabled = False
    LoadModelsGroupBox_Layout.addRow("Model Path: ", self.modelsPathEdit)

    # Button to load model
    self.loadModelButton = qt.QPushButton("Load Model")
    self.loadModelButton.toolTip = "Load Model"
    self.loadModelButton.enabled = False
    LoadModelsGroupBox_Layout.addRow(self.loadModelButton)

    # Create List
    self.modelsListWidget = qt.QListWidget()
    LoadModelsGroupBox_Layout.addRow(self.modelsListWidget)

    # Create buttons to delete models o delete all
    deleteOneOrAllModels_Layout = qt.QHBoxLayout()
    LoadModelsGroupBox_Layout.addRow(deleteOneOrAllModels_Layout)

    self.removeSelectedModelButton = qt.QPushButton("Remove Model")
    self.removeSelectedModelButton.enabled = False
    deleteOneOrAllModels_Layout.addWidget(self.removeSelectedModelButton)
    
    self.removeAllModelsButton = qt.QPushButton("Remove All")
    self.removeAllModelsButton.enabled = False
    deleteOneOrAllModels_Layout.addWidget(self.removeAllModelsButton) 

    # Button to move models to origin
    self.moveToOriginlButton = qt.QPushButton("Finish and Center")
    self.moveToOriginlButton.enabled = False
    formLayout_init.addRow(self.moveToOriginlButton)
    # self.layout.addStretch(1)

    #-------------------------------------------------------#
    #------------------- Positioning -----------------------#
    #-------------------------------------------------------#

    # Creacion layout
    self.collapsibleButtonPos = ctk.ctkCollapsibleButton()
    self.collapsibleButtonPos.text = "POSITIONING"
    self.collapsibleButtonPos.collapsed = True
    # self.collapsibleButtonPos.enabled = False
    self.layout.addWidget(self.collapsibleButtonPos)

    formLayout_pos = qt.QFormLayout(self.collapsibleButtonPos) 
    ## Base Model Height
    self.BaseGroupBox = ctk.ctkCollapsibleGroupBox()
    self.BaseGroupBox.setTitle("AR Marker Adaptor Height")
    self.BaseGroupBox.visible = False
    formLayout_pos.addRow(self.BaseGroupBox)
    BaseGroupBox_Layout = qt.QFormLayout(self.BaseGroupBox)

    self.baseHeightSliderWidget = ctk.ctkSliderWidget()
    self.baseHeightSliderWidget.singleStep = 10
    self.baseHeightSliderWidget.minimum = 10
    self.baseHeightSliderWidget.maximum = 50
    self.baseHeightSliderWidget.value = 10
    BaseGroupBox_Layout.addRow("[mm]: ", self.baseHeightSliderWidget)

    ## Slider Scale
    ScaleGroupBox = ctk.ctkCollapsibleGroupBox()
    ScaleGroupBox.setTitle("Scale")
    formLayout_pos.addRow(ScaleGroupBox)
    ScaleGroupBox_Layout = qt.QFormLayout(ScaleGroupBox)

    self.scaleSliderWidget = ctk.ctkSliderWidget()
    self.scaleSliderWidget.singleStep = 1
    self.scaleSliderWidget.minimum = 0.0000000001
    self.scaleSliderWidget.maximum = 500
    self.scaleSliderWidget.value = 100
    ScaleGroupBox_Layout.addRow("[%]: ", self.scaleSliderWidget)

    ## Slider Translation

    TranslationGroupBox = ctk.ctkCollapsibleGroupBox()
    TranslationGroupBox.setTitle("Translation")
    formLayout_pos.addRow(TranslationGroupBox)
    TranlationGroupBox_Layout = qt.QFormLayout(TranslationGroupBox)

    self.lrTranslationSliderWidget = ctk.ctkSliderWidget()
    self.lrTranslationSliderWidget.singleStep = 0.5
    self.lrTranslationSliderWidget.minimum = -1000
    self.lrTranslationSliderWidget.maximum = 1000
    self.lrTranslationSliderWidget.value = 0
    self.lrTranslationSliderWidget.setToolTip("Z Translation Transform")
    TranlationGroupBox_Layout.addRow("LR: ", self.lrTranslationSliderWidget)

    self.paTranslationSliderWidget = ctk.ctkSliderWidget()
    self.paTranslationSliderWidget.singleStep = 0.5
    self.paTranslationSliderWidget.minimum = -1000
    self.paTranslationSliderWidget.maximum = 1000
    self.paTranslationSliderWidget.value = 0
    self.paTranslationSliderWidget.setToolTip("Z Translation Transform")
    TranlationGroupBox_Layout.addRow("PA: ", self.paTranslationSliderWidget)

    self.isTranslationSliderWidget = ctk.ctkSliderWidget()
    self.isTranslationSliderWidget.singleStep = 0.5
    self.isTranslationSliderWidget.minimum = -1000
    self.isTranslationSliderWidget.maximum = 1000
    self.isTranslationSliderWidget.value = 0
    self.isTranslationSliderWidget.setToolTip("Z Translation Transform")
    TranlationGroupBox_Layout.addRow("IS: ", self.isTranslationSliderWidget)
    
    ## Slider Rotation
    RotationGroupBox = ctk.ctkCollapsibleGroupBox()
    RotationGroupBox.setTitle("Rotation")
    formLayout_pos.addRow(RotationGroupBox)
    RotationGroupBox_Layout = qt.QFormLayout(RotationGroupBox)

    self.lrRotationSliderWidget = ctk.ctkSliderWidget()
    self.lrRotationSliderWidget.singleStep = 1
    self.lrRotationSliderWidget.minimum = -180
    self.lrRotationSliderWidget.maximum = 180
    self.lrRotationSliderWidget.value = 0
    self.lrRotationSliderWidget.setToolTip("LR Rotation")
    RotationGroupBox_Layout.addRow("LR: ", self.lrRotationSliderWidget)

    self.paRotationSliderWidget = ctk.ctkSliderWidget()
    self.paRotationSliderWidget.singleStep = 1
    self.paRotationSliderWidget.minimum = -180
    self.paRotationSliderWidget.maximum = 180
    self.paRotationSliderWidget.value = 0
    self.paRotationSliderWidget.setToolTip("PA Rotation")
    RotationGroupBox_Layout.addRow("PA: ", self.paRotationSliderWidget)

    self.isRotationSliderWidget = ctk.ctkSliderWidget()
    self.isRotationSliderWidget.singleStep = 1
    self.isRotationSliderWidget.minimum = -180
    self.isRotationSliderWidget.maximum = 180
    self.isRotationSliderWidget.value = 0
    self.isRotationSliderWidget.setToolTip("IS Rotation")
    RotationGroupBox_Layout.addRow("IS: ", self.isRotationSliderWidget)

    ## Button reset
    self.resetPosButton = qt.QPushButton("Reset Position")
    self.resetPosButton.enabled = True
    formLayout_pos.addRow(self.resetPosButton) 

    """
    #-------------------------------------------------------#
    #------------------- Appereance -----------------------#
    #-------------------------------------------------------#

    # Init layout
    collapsibleButtonAppereance = ctk.ctkCollapsibleButton()
    collapsibleButtonAppereance.text = "Appereance"
    self.layout.addWidget(collapsibleButtonAppereance)
    formLayout_init = qt.QFormLayout(collapsibleButtonAppereance)
    """

    #-------------------------------------------------------#
    #------------------- Save Models -----------------------#
    #-------------------------------------------------------#

    # Init layout
    self.collapsibleButtonSaveModels = ctk.ctkCollapsibleButton()
    self.collapsibleButtonSaveModels.text = "SAVE MODELS"
    self.collapsibleButtonSaveModels.collapsed = True
    self.layout.addWidget(self.collapsibleButtonSaveModels)
    formLayout_init = qt.QFormLayout(self.collapsibleButtonSaveModels)

    # Data Stream File Path Selector
    self.saveDirectoryButton = ctk.ctkDirectoryButton()
    formLayout_init.addRow("Save Model Path: ", self.saveDirectoryButton)

    # Button to load model
    self.saveModelButton = qt.QPushButton("Save Models")
    self.saveModelButton.toolTip = "Save Models"
    self.saveModelButton.enabled = False
    formLayout_init.addRow(self.saveModelButton) # incluimos el boton al layout

    self.layout.addStretch(1)

    #########################################################################################
    #########################################################################################
    #########################################################################################

    # Connections
    self.resetButton.connect("clicked(bool)", self.onResetButton)
    self.mode1_radioButton.connect('clicked(bool)', self.onModeSelected)
    self.mode2_radioButton.connect('clicked(bool)', self.onModeSelected)
    self.loadMarkerButton.connect("clicked(bool)", self.onLoadMarkerButton)
    self.loadModelButton.connect("clicked(bool)", self.onLoadModelsButton)
    self.removeSelectedModelButton.connect("clicked(bool)", self.onRemoveSelectedModelButton)
    self.removeAllModelsButton.connect("clicked(bool)", self.onRemoveAllModelsButton)
    self.moveToOriginlButton.connect("clicked(bool)", self.onMoveToOriginlButton)
    self.baseHeightSliderWidget.connect("valueChanged(double)", self.onBaseHeightSliderWidgetChanged)
    self.scaleSliderWidget.connect("valueChanged(double)", self.onScaleSliderWidgetChanged)
    self.lrTranslationSliderWidget.connect("valueChanged(double)", self.onLRTranslationSliderWidgetChanged)
    self.paTranslationSliderWidget.connect("valueChanged(double)", self.onPATranslationSliderWidgetChanged)
    self.isTranslationSliderWidget.connect("valueChanged(double)", self.onISTranslationSliderWidgetChanged)
    self.lrRotationSliderWidget.connect("valueChanged(double)", self.onLRRotationSliderWidgetChanged)
    self.paRotationSliderWidget.connect("valueChanged(double)", self.onPARotationSliderWidgetChanged)
    self.isRotationSliderWidget.connect("valueChanged(double)", self.onISRotationSliderWidgetChanged)
    self.resetPosButton.connect("clicked(bool)", self.onResetPosButton)
    self.saveModelButton.connect("clicked(bool)", self.onsaveModelButton) 


  def onResetButton(self):

    # Reset GUI
    # Mode selection
    self.modeSelection_GroupBox.enabled = True
    self.mode1_radioButton.checked = True
    self.mode2_radioButton.checked = False
    self.loadMarkerButton.enabled = True
    self.modelsPathEdit.enabled = False
    self.loadModelButton.enabled = False
    self.removeSelectedModelButton.enabled = False
    self.removeAllModelsButton.enabled = False
    self.moveToOriginlButton.enabled = False
    self.collapsibleButtonPos.collapsed = True
    self.BaseGroupBox.visible = False
    self.resetPosButton.enabled = True
    self.collapsibleButtonSaveModels.collapsed = True
    self.saveModelButton.enabled = False
    
    # Reset variables
    self.logic.resetVariables()


  def onModeSelected(self):

    # Update selected mode
    if self.mode1_radioButton.isChecked():
        print 'Option 1 selected' 
        self.logic.selected_mode = 1
        self.BaseGroupBox.visible = False

    if self.mode2_radioButton.isChecked():
        print 'Option 2 selected' 
        self.logic.selected_mode = 2        
        self.BaseGroupBox.visible = True

  def onLoadMarkerButton(self):
    """
    Load Maker
    """
    print("loading marker...")
    self.logic.loadMarker()
    print("Marker Loaded.")

    self.loadMarkerButton.enabled = False
    self.modelsPathEdit.enabled = True
    self.loadModelButton.enabled = True
    self.modeSelection_GroupBox.enabled = False

  def onLoadModelsButton(self):
    """
    Load Models
    """
    print("Loading model...")
    modelsPath = self.modelsPathEdit.currentPath
    print("lala", modelsPath)
    
    if modelsPath != "":
      print("He entrado en load model")
      model_name = self.logic.loadModels(modelsPath)

      if model_name is not None:
        self.addModelToList(model_name)

      self.modelsPathEdit.currentPath = ""
      self.moveToOriginlButton.enabled = True
      self.removeSelectedModelButton.enabled = True
      self.removeAllModelsButton.enabled = True

  def onRemoveSelectedModelButton(self):
    """
    """
    try:
      selected_model_item = self.modelsListWidget.selectedItems()[0]
      selected_model_name = selected_model_item.text()
      selected_model_item.delete()

      self.logic.removeModel(selected_model_name)

      print("Model {} has been rmeoved.".format(selected_model_name))


    except IndexError:
      pass

  def onRemoveAllModelsButton(self):
    """
    """
    try:
      self.modelsListWidget.clear()
      self.logic.removeAllModels()

      print("All Models have been rmeoved.")

      self.moveToOriginlButton.enabled = False

    except IndexError:
      pass

  def onMoveToOriginlButton(self):
    """
    """
    self.logic.moveModelsToOrigin()

    self.collapsibleButtonInit.collapsed = True
    self.modelsPathEdit.enabled = False
    self.loadModelButton.enabled = False
    self.collapsibleButtonPos.collapsed = False
    self.collapsibleButtonSaveModels.collapsed = False
    self.saveModelButton.enabled = True

  def onBaseHeightSliderWidgetChanged(self):

    # Get value
    self.logic.baseHeightMode_val = self.baseHeightSliderWidget.value

    # Update virtual camera transform
    self.logic.updateBaseHeightModel()

  def onScaleSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.scaleVal = self.scaleSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsScale()

  def onLRTranslationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.translation_LR = self.lrTranslationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsTranslation()

  def onPATranslationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.translation_PA = self.paTranslationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsTranslation()
    
  def onISTranslationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.translation_IS = self.isTranslationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsTranslation()

  def onLRRotationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.rotation_LR = self.lrRotationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsRotation()

  def onPARotationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.rotation_PA = self.paRotationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsRotation()

  def onISRotationSliderWidgetChanged(self):
    """
    """
    # Get value
    self.logic.rotation_IS = self.isRotationSliderWidget.value

    # Update virtual camera transform
    self.logic.updateModelsRotation()

  def onResetPosButton(self):
    """
    """
    self.logic.resetPositioningTransform()

    ## Scale
    self.scaleSliderWidget.value = 100.0
    # Translation
    self.lrTranslationSliderWidget.value = 0.0
    self.paTranslationSliderWidget.value = 0.0
    self.isTranslationSliderWidget.value = 0.0
    #Rotation
    self.lrRotationSliderWidget.value = 0.0
    self.paRotationSliderWidget.value = 0.0
    self.isRotationSliderWidget.value = 0.0

  def onsaveModelButton(self):
    """
    """
    save_folder_path = self.saveDirectoryButton.directory
    print("Save Folder Path:", save_folder_path)
    self.logic.saveModels(save_folder_path)


  def setCustomLayout(self):
      layoutLogic = self.layoutManager.layoutLogic()
      customLayout_1 = ("<layout type=\"horizontal\">"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "   <property name=\"viewlabel\" action=\"default\">1</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_2 = ("<layout type=\"horizontal\" split=\"true\">"
      " <item>"
      "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Yellow\">"
      "   <property name=\"orientation\" action=\"default\">Sagittal</property>"
      "   <property name=\"viewlabel\" action=\"default\">Y</property>"
      "   <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "  </view>"
      " </item>"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "  <property name=\"viewlabel\" action=\"default\">T</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_3 = ("<layout type=\"horizontal\">"
      " <item>"
      "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "   <property name=\"orientation\" action=\"default\">Axial</property>"
      "     <property name=\"viewlabel\" action=\"default\">R</property>"
      "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
      "  </view>"
      " </item>"
      "</layout>")
      customLayout_4 = ("<layout type=\"horizontal\" split=\"false\">"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
      "  <property name=\"viewlabel\" action=\"default\">1</property>"
      "  </view>"
      " </item>"
      " <item>"
      "  <view class=\"vtkMRMLViewNode\" singletontag=\"2\">"
      "  <property name=\"viewlabel\" action=\"default\">2</property>"
      "  </view>"
      " </item>"
      "</layout>")
      self.customLayout_1_ID=996
      self.customLayout_2_ID=997
      self.customLayout_3_ID=998
      self.customLayout_4_ID=999
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_1_ID, customLayout_1)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_2_ID, customLayout_2)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_3_ID, customLayout_3)
      layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_4_ID, customLayout_4)

  def addModelToList(self, model_name):
    """
    """
    self.modelsListWidget.addItem(model_name)

  def deleteModelFromList(self, model_name):
    self.modelsListWidget

#
# ARHealth LOGIC
#
class ARHealthLogic(ScriptedLoadableModuleLogic):


  def __init__(self):

    self.models_path = slicer.modules.arhealth.path.replace("ARHealth.py", "") + "Resources/Models/"
    self.models = dict()

    # Mode
    self.selected_mode = 1

    # Center Model Transform
    self.centerModelsTransform = slicer.vtkMRMLLinearTransformNode()
    self.centerModelsTransform.SetName("centerModelsTransform")
    slicer.mrmlScene.AddNode(self.centerModelsTransform)

    # Base height
    self.baseHeightMode_val = 10

    # Scaling
    self.scaleTransform = slicer.vtkMRMLLinearTransformNode()
    self.scaleTransform.SetName("scaleTransform")
    slicer.mrmlScene.AddNode(self.scaleTransform)

    self.scaleVal = 100.0

    # Translation
    self.translationTransform = slicer.vtkMRMLLinearTransformNode()
    self.translationTransform.SetName("translationTransform")
    slicer.mrmlScene.AddNode(self.translationTransform)

    self.translation_PA = 0.0
    self.translation_LR = 0.0
    self.translation_IS = 0.0

    # Rotation
    self.rotationTransform = slicer.vtkMRMLLinearTransformNode()
    self.rotationTransform.SetName("rotationTransform")
    slicer.mrmlScene.AddNode(self.rotationTransform)
    
    self.rotation_LR = 0.0
    self.rotation_PA = 0.0
    self.rotation_IS = 0.0

    # Positioning Transform
    self.positioningTransform = slicer.vtkMRMLLinearTransformNode()
    self.positioningTransform.SetName("positioningTransform")
    slicer.mrmlScene.AddNode(self.positioningTransform)

    # Color code
    self.color_code_i = 0

  def resetVariables(self):

    self.models_path = slicer.modules.arhealth.path.replace("ARHealth.py", "") + "Resources/Models/"
    self.models = dict()

    # Mode
    self.selected_mode = 1

    # Center Model Transform
    slicer.mrmlScene.RemoveNode(self.centerModelsTransform)
    self.centerModelsTransform = slicer.vtkMRMLLinearTransformNode()
    self.centerModelsTransform.SetName("centerModelsTransform")
    slicer.mrmlScene.AddNode(self.centerModelsTransform)

    # Base height
    self.baseHeightMode_val = 10

    # Scaling
    slicer.mrmlScene.RemoveNode(self.scaleTransform)
    self.scaleTransform = slicer.vtkMRMLLinearTransformNode()
    self.scaleTransform.SetName("scaleTransform")
    slicer.mrmlScene.AddNode(self.scaleTransform)

    self.scaleVal = 100.0

    # Translation
    slicer.mrmlScene.RemoveNode(self.translationTransform)
    self.translationTransform = slicer.vtkMRMLLinearTransformNode()
    self.translationTransform.SetName("translationTransform")
    slicer.mrmlScene.AddNode(self.translationTransform)

    self.translation_PA = 0.0
    self.translation_LR = 0.0
    self.translation_IS = 0.0

    # Rotation
    slicer.mrmlScene.RemoveNode(self.rotationTransform)
    self.rotationTransform = slicer.vtkMRMLLinearTransformNode()
    self.rotationTransform.SetName("rotationTransform")
    slicer.mrmlScene.AddNode(self.rotationTransform)
    
    self.rotation_LR = 0.0
    self.rotation_PA = 0.0
    self.rotation_IS = 0.0

    # Positioning Transform
    slicer.mrmlScene.RemoveNode(self.positioningTransform)
    self.positioningTransform = slicer.vtkMRMLLinearTransformNode()
    self.positioningTransform.SetName("positioningTransform")
    slicer.mrmlScene.AddNode(self.positioningTransform)

    # Color code
    self.color_code_i = 0

  def loadMarker(self):

    try:
        self.marker_white = slicer.util.getNode("Marker_Cube_White")
        self.marker_black = slicer.util.getNode("Marker_Cube_Black")
        if self.selected_mode == 1:
            self.base_table = silcer.util.getNode("ARHealth_BaseTable")
        self.base_model = slicer.util.getNode("ARHealth_BaseModel")
        self.center3DView()

    except:
        # Load white part
        path_aux = self.models_path + "Marker_Cube_White.obj"
        self.marker_white = self.loadNewModel(path_aux, color_code=[1,1,1])
        # [success, self.marker_white] = slicer.util.loadModel(self.models_path + "Marker_Cube_White.stl", returnNode=True)
        # self.marker_white.GetModelDisplayNode().SetColor([0,0,0])
        
        # Load black part
        path_aux = self.models_path + "Marker_Cube_Black.obj"
        self.marker_black = self.loadNewModel(path_aux, color_code=[0,0,0])
        # [success, self.marker_black] = slicer.util.loadModel(self.models_path + "Marker_Cube_Black.stl", returnNode=True)
        # self.marker_black.GetModelDisplayNode().SetColor([1,1,1])

        if self.selected_mode == 1:

            # Load Base Table
            path_aux = self.models_path + "ARHealth_BaseTable.obj"
            self.base_table = self.loadNewModel(path_aux, color_code=[1,1,1])

            # Load Base Model
            path_aux = self.models_path + "ARHealth_BaseModel_2mm.stl"
            self.base_model = self.loadNewModel(path_aux, color_code=[1,1,1])

        elif self.selected_mode == 2:
            # Load Base Model
            path_aux = self.models_path + "ARHealth_BaseModel_10mm.stl"
            self.base_model = self.loadNewModel(path_aux, color_code=[1,1,1])

        # self.base_model.GetDisplayNode().SetVisibility(True)

        self.center3DView()

  def loadModels(self, modelPath):
    """
    Load Models into scene
    """
    model_name = modelPath.split("/")[-1]


    if model_name not in self.models.keys():
      self.models[model_name] = dict()

      self.models[model_name]["path"] = modelPath

      #[success, model_aux] = slicer.util.loadModel(modelPath, returnNode=True)
      #model_aux.GetModelDisplayNode().SetColor([0,0.5,0])

      self.models[model_name]["node"] = self.loadNewModel(modelPath, color_code=self.color_code())
      # self.buildTransformTree(self.models[model_name]["node"])

      # Center 3D view
      self.center3DView()

      print("New Model loaded.")

      return model_name

    else:
      print("Model already loaded.")
      return None

  def loadNewModel(self, path, color_code=[0,0.5,0]):
    """
    """
    [success, model] = slicer.util.loadModel(path, returnNode=True)
    model.GetModelDisplayNode().SetColor(color_code)
    return model

  def removeModel(self, model_name):
    """
    """
    if model_name in self.models.keys():
      model_node = self.models[model_name]["node"]
      slicer.mrmlScene.RemoveNode(model_node)
      self.models.pop(model_name, None)
      self.center3DView()

  def removeAllModels(self):
    """
    """
    for model_name in self.models.keys():
      self.removeModel(model_name)
    self.center3DView()
    self.models = dict()

  def moveModelsToOrigin(self):
    """
    """
    box = np.zeros(6)

    # Get Bounding box of all models
    for i, model_name in enumerate(self.models.keys()):
      modelNode = self.models[model_name]["node"]
      a = np.zeros(6)
      modelNode.GetRASBounds(a)
      if i == 0:
        box = a
      else:
        minimums = np.minimum(box, a)
        maximums = np.maximum(box, a)
        box[[0,2,4]] = minimums[[0,2,4]]
        box[[1,3,5]] = maximums[[1,3,5]]
      print(a)
      modelNode.SetAndObserveTransformNodeID(self.centerModelsTransform.GetID())
    print(box)

    # Create Move to Origin Transform from box
    center = self.get_center_from_box(box)
    vTransform = vtk.vtkTransform()
    vTransform.Translate(-center[0],-center[1],-center[2]) 
    self.centerModelsTransform.SetMatrixTransformToParent(vTransform.GetMatrix())

    # Harden
    for i, model_name in enumerate(self.models.keys()):
      modelNode = self.models[model_name]["node"]
      modelNode.HardenTransform()

    # Move models to Positioing Transform Tree
    self.buildPositioningTransformTreeAllModels()

    # Center 3D view
    self.center3DView()

  def get_center_from_box(self, box):
    center = [0.0, 0.0, 0.0]
    center[0] = box[[0,1]].mean()
    center[1] = box[[2,3]].mean()
    center[2] = box[[4,5]].mean()
    return center

  def buildPositioningTransformTreeAllModels(self):
    """
    """
    for i, model_name in enumerate(self.models.keys()):
      modelNode = self.models[model_name]["node"]
      self.buildPositioningTransformTree(modelNode)

  def buildPositioningTransformTree(self, modelNode):
    """
    """
    modelNode.SetAndObserveTransformNodeID(self.scaleTransform.GetID())
    self.scaleTransform.SetAndObserveTransformNodeID(self.rotationTransform.GetID())
    self.rotationTransform.SetAndObserveTransformNodeID(self.translationTransform.GetID())

  def resetPositioningTransform(self):
    matrix = vtk.vtkMatrix4x4()
    self.scaleTransform.SetMatrixTransformToParent(matrix)
    self.translationTransform.SetMatrixTransformToParent(matrix)
    self.rotationTransform.SetMatrixTransformToParent(matrix)

  def updateBaseHeightModel(self):

    baseHeightMode_val = self.baseHeightMode_val

    # Remove node from scene
    slicer.mrmlScene.RemoveNode(self.base_model)

    # Load Base Model
    path_aux = self.models_path + "ARHealth_BaseModel_" + str(int(self.baseHeightMode_val)) + "mm.stl"
    self.base_model = self.loadNewModel(path_aux, color_code=[1,1,1])
    self.base_model.GetDisplayNode().SetVisibility(True)

  def updateModelsScale(self):
    """
    """
    vTransform = vtk.vtkTransform()
    vTransform.Scale(self.scaleVal/100., self.scaleVal/100., self.scaleVal/100.) 
    self.scaleTransform.SetMatrixTransformToParent(vTransform.GetMatrix())

  def updateModelsTranslation(self):
    """
    """
    vTransform = vtk.vtkTransform()
    vTransform.Translate(self.translation_LR, self.translation_PA, self.translation_IS) 
    self.translationTransform.SetMatrixTransformToParent(vTransform.GetMatrix())

  def updateModelsRotation(self):
    """
    """
    rotMatrix = vtk.vtkTransform()
    rotMatrix.RotateX(self.rotation_LR) 
    rotMatrix.RotateY(self.rotation_PA) 
    rotMatrix.RotateZ(self.rotation_IS) 
    self.rotationTransform.SetMatrixTransformToParent(rotMatrix.GetMatrix())

  def center3DView(self):
    """
    """
    # Center 3D view
    layoutManager = slicer.app.layoutManager()
    threeDWidget = layoutManager.threeDWidget(0)
    threeDView = threeDWidget.threeDView()
    threeDView.resetFocalPoint()

  def saveModels(self, save_folder_path):
    """
    """
    for i, model_name in enumerate(self.models.keys()):
      modelNode = self.models[model_name]["node"]
      # make a copy of the model and apply the transforms
      modelNode_copy,hardened_transform = self.copyAndHardenModel(modelNode)
      # save model
      file_name = "{}_registered.obj".format(model_name.split(".")[0])      
      path_aux = os.path.join(save_folder_path, file_name)
      slicer.util.saveNode(modelNode_copy, path_aux)
      # undo transforms in model
      hardened_transform.Inverse()
      modelNode_copy.SetAndObserveTransformNodeID(hardened_transform.GetID())
      modelNode_copy.HardenTransform()
      slicer.mrmlScene.RemoveNode(modelNode_copy)
      slicer.mrmlScene.RemoveNode(hardened_transform)

    # Save Adaptor
    if self.selected_mode == 2: # Biomodel Registration mode
        path_aux = os.path.join(save_folder_path, "ARHealth_BaseModel.obj")
        slicer.util.saveNode(self.base_model, path_aux)

    # Save Transforms
    self.positioningTransform.SetAndObserveTransformNodeID(self.centerModelsTransform.GetID())
    self.positioningTransform.HardenTransform()
    self.positioningTransform.SetAndObserveTransformNodeID(self.scaleTransform.GetID())
    self.positioningTransform.HardenTransform()

    self.saveData("positioningTransform", save_folder_path, "fromModelToMarkerTransform.h5")

    print('All models have been saved.')

  def copyAndHardenModel(self,originalModel):
    # copy model
    outputModel = slicer.vtkMRMLModelNode()
    fullPolyData = originalModel.GetPolyData()
    outputModel.SetAndObservePolyData(fullPolyData)
    md2 = slicer.vtkMRMLModelDisplayNode()
    slicer.mrmlScene.AddNode(outputModel)
    slicer.mrmlScene.AddNode(md2)
    outputModel.SetAndObserveDisplayNodeID(md2.GetID())
    md2.SetVisibility(0)
    # apply transforms tree to copied model
    parent_transform = originalModel.GetParentTransformNode()
    try:
        t = slicer.util.getNode('DefinedTransform')
        identityTransform = vtk.vtkMatrix4x4()
        t.SetMatrixTransformToParent(identityTransform)
    except:
        t=slicer.vtkMRMLLinearTransformNode()
        t.SetName('DefinedTransform')
        slicer.mrmlScene.AddNode(t)
    t.SetAndObserveTransformNodeID(parent_transform.GetID())
    t.HardenTransform()
    outputModel.SetAndObserveTransformNodeID(t.GetID())
    outputModel.HardenTransform()
    return outputModel,t


  def saveData(self, node_name, folder_path, file_name):
    # Save node to path
    node = slicer.util.getNode(node_name)
    path = os.path.join(folder_path, file_name)
    return slicer.util.saveNode(node, path)

  def color_code(self):
    color_code, reset = self.get_color_code(self.color_code_i)

    if reset:
      self.color_code_i = 0
    else:
      self.color_code_i += 1

    return color_code

  def get_color_code(self, id):
    reset = False
    color_codes = [
      [0.5, 0.0, 0.0],
      [0.0, 0.5, 0.0],
      [0.0, 0.0, 0.5],
      [0.5, 0.5, 0.0],
      [0.0, 0.5, 0.5],
      [0.5, 0.0, 0.5],
      [0.5, 0.5, 0.5]
    ]
    if id == (len(color_codes)-1):
      reset = True

    return color_codes[id], reset

  def merge_models(self, modelA, modelB, modelC):

    scene = slicer.mrmlScene

    # Create model node
    mergedModel = slicer.vtkMRMLModelNode()
    mergedModel.SetScene(scene)
    mergedModel.SetName(modelName)
    dnode = slicer.vtkMRMLModelDisplayNode()
    snode = slicer.vtkMRMLModelStorageNode()
    mergedModel.SetAndObserveDisplayNodeID(dnode.GetID())
    mergedModel.SetAndObserveStorageNodeID(snode.GetID())
    scene.AddNode(dnode)
    scene.AddNode(snode)
    scene.AddNode(mergedModel)

    # Get transformed poly data from input models
    modelA_polydata = self.getTransformedPolyDataFromModel(self.modelA)
    modelB_polydata = self.getTransformedPolyDataFromModel(self.modelB)
    modelC_polydata = self.getTransformedPolyDataFromModel(self.modelC)
    
    # Append poly data
    appendFilter = vtk.vtkAppendPolyData()
    appendFilter.AddInputData(modelA_polydata)
    appendFilter.AddInputData(modelB_polydata)
    appendFilter.AddInputData(modelC_polydata)
    appendFilter.Update();

    # Output
    mergedModel.SetAndObservePolyData(appendFilter.GetOutput());
    mergedModel.SetAndObserveDisplayNodeID(dnode.GetID());

    return mergedModel
  