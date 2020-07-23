from __future__ import division
from __future__ import print_function
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.path.join('Resources','Libraries')))
import numpy as np
from scipy import stats

import MFSDA_stat as mfsda
import timeit
import argparse
import json
import os.path
import csv 
import time

#
# MFSDA
#

class MFSDA(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Covariate Significance Testing" # TODO make this more human readable by adding spaces
        self.parent.categories = ["Shape Analysis"]
        self.parent.dependencies = []
        self.parent.contributors = ["Loic Michoud"] # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
        This is an example of scripted loadable module bundled in an extension.
        It performs a simple thresholding on the input volume and optionally captures a screenshot.
        """
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
        This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
        and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
        """ # replace with organization, grant and thanks.

#
# MFSDAWidget
#

class MFSDAWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # test=False
        self.logic = MFSDALogic(self)
        # self.test = MFSDATest(self)
        self.moduleName = 'MFSDA'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
        self.widget = slicer.util.loadUI(path)
        self.layout.addWidget(self.widget)
        # Instantiate and connect widgets ...
        self.stateCSVMeansShape = False
        self.dictShapeModels = dict()
        
        self.lineEdit_csv = self.logic.get('lineEdit_csv')
        self.tableWidget = self.logic.get('tableWidget')
        self.lineEdit_pshape = self.logic.get('lineEdit_pshape')
        self.lineEdit_output = self.logic.get('lineEdit_output')

        self.pushButton_run = self.logic.get('pushButton_run')

        '''
        self.lineEdit_pshape.connect('currentPathChanged(const QString)', self.onCSVFile)
        self.lineEdit_csv.connect('currentPathChanged(const QString)', self.onCSVFile)
        self.lineEdit_output.connect('directoryChanged (const QString)', self.onCSVFile)'''    
        self.lineEdit_csv.connect('currentPathChanged(const QString)', self.onCSVFile)
        self.pushButton_run.connect('clicked(bool)', self.onCSVFile)


    def onShapeState(self):
        state=self.MFSDAShapeThread.GetStatusString()
        if state=='Running'or state=='Scheduled':
            seconds = time.time()-self.starting_time
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h==0 and m==0:
                t = "00:%02d" % (s)
            elif h==0 :
                t = "%02d:%02d" % (m, s)
            else:
                t = "%d:%02d:%02d" % (h, m, s)
            if int(s) ==0:
                print("MFSDA shape creation "+self.MFSDAShapeThread.GetStatusString()+"  "+t)

            self.pushButton_run.setText("Abort shape creation ("+t+")")
        else:
            print('MFSDA shape creation done')
            self.checkThreadTimer.stop()
            self.checkThreadTimer.disconnect('timeout()', self.onShapeState)

            CSVFile=open(self.lineEdit_output.directory+'/output.csv', 'w')
            Data=['VTK Files']
            with CSVFile:
                writer = csv.writer(CSVFile)
                writer.writerow(Data)
                writer.writerow([self.lineEdit_output.directory + '/out.vtk'])
            CSVFile.close()
            self.pushButton_run.setText("Run")
            self.pushButton_run.connect('clicked(bool)', self.onCSVFile)
            self.pushButton_run.disconnect('clicked(bool)', self.onKillComputationShape)
            parameters = {}
            csvFilePath = self.lineEdit_output.directory+'/output.csv'
            slicer.modules.shapepopulationviewer.widgetRepresentation().loadCSVFile(csvFilePath)
            slicer.util.selectModule(slicer.modules.shapepopulationviewer)


        return

    def onKillComputationShape(self):
        
        self.pushButton_run.clicked.disconnect()
        self.pushButton_run.connect('clicked()',self.onCSVFile)
        self.pushButton_run.setText("Run")

        self.checkThreadTimer.stop()
        self.checkThreadTimer.timeout.disconnect()

        self.MFSDAShapeThread.Cancel()
        minutes = int((time.time()-self.starting_time)/60)
        print('Computation Stopped after '+str(minutes)+' min')


    def onComputationState(self):
        state=self.MFSDAThread.GetStatusString()
        if state=='Running'or state=='Scheduled':
            seconds = time.time()-self.starting_time
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h==0 and m==0:
                t = "00:%02d" % (s)
            elif h==0 :
                t = "%02d:%02d" % (m, s)
            else:
                t = "%d:%02d:%02d" % (h, m, s)
            if int(s) ==0:
                print("MFSDA computation "+self.MFSDAThread.GetStatusString()+"  "+t)

            self.pushButton_run.setText("Abort computation ("+t+")")
        else:
            print('MFSDA Computation done')
            self.checkThreadTimer.stop()

            # Read covariate names from first line of csv
            f = open(self.lineEdit_csv.currentPath)
            covariate_names = [ x.strip() for x in f.readline().split(',')[1:] ]

            self.param = {}
            self.param["shape"] = self.lineEdit_pshape.currentPath
            self.param["pvalues"] = self.lineEdit_output.directory+'/pvalues.json'
            self.param["efit"] = self.lineEdit_output.directory+'/efit.json'
            self.param["covariates"] = ' '.join(covariate_names)
            self.param["output"] = self.lineEdit_output.directory+'/out.vtk'

            MFSDAShapemodule = slicer.modules.mfsda_createshapes
            self.MFSDAShapeThread=slicer.cli.run(MFSDAShapemodule, None, self.param, wait_for_completion=False)

            
            self.checkThreadTimer.disconnect('timeout()', self.onComputationState)
            self.checkThreadTimer.connect('timeout()', self.onShapeState)
            self.checkThreadTimer.start(1000)

            self.pushButton_run.connect('clicked(bool)', self.onKillComputationShape)
            self.pushButton_run.disconnect('clicked(bool)', self.onKillComputation)


    def onKillComputation(self):
        
        self.pushButton_run.clicked.disconnect()
        self.pushButton_run.connect('clicked()',self.onCSVFile)
        self.pushButton_run.setText("Run")

        self.checkThreadTimer.stop()
        self.checkThreadTimer.timeout.disconnect()

        self.MFSDAThread.Cancel()
        minutes = int((time.time()-self.starting_time)/60)
        print('Computation Stopped after '+str(minutes)+' min')

    def onCSVFile(self):
        self.dictShapeModels = dict()
        '''if not os.path.exists(self.lineEdit_covariateType.currentPath):
            self.stateCSVMeansShape = False
            return'''
        if not os.path.exists(self.lineEdit_csv.currentPath):
            self.stateCSVMeansShape = False
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)
            return
        
        condition1 = self.logic.checkExtension(self.lineEdit_csv.currentPath, ".csv")

        if condition1:
            f = open(self.lineEdit_csv.currentPath)
            headers = [ x.strip() for x in f.readline().split(',') ]
            self.tableWidget.setColumnCount(len(headers))
            self.tableWidget.setHorizontalHeaderLabels(headers)
            row = 0
            for line in f.readlines():
                vals = [ x.strip() for x in line.split(',') ]
                self.tableWidget.insertRow(row)
                for col in range(len(vals)):
                    widget = qt.QWidget()
                    layout = qt.QHBoxLayout(widget)
                    label = qt.QLabel()
                    label.setText(vals[col])
                    
                    layout.addWidget(label)
                    layout.setAlignment(0x84)
                    layout.setContentsMargins(0,0,0,0)
                    widget.setLayout(layout)
                    self.tableWidget.setCellWidget(row,col,widget)
                row = row + 1
        else:
            self.lineEdit_csv.setCurrentPath(" ")
            self.stateCSVDataset = False
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)
            return

        if not os.path.exists(self.lineEdit_pshape.currentPath):
            self.stateCSVMeansShape = False
            return
        if not os.path.exists(self.lineEdit_output.directory):
            self.stateCSVMeansShape = False
            return
        """if not os.path.exists(self.lineEdit_CovariateNames.currentPath):
            self.stateCSVMeansShape = False
            return"""
        
        condition2 = self.logic.checkExtension(self.lineEdit_pshape.currentPath, ".vtk")
        condition3 = self.lineEdit_output.directory != '.'

        if not condition2:
            self.lineEdit_pshape.setCurrentPath(" ")
            self.stateCSVDataset = False
            return
        if not condition3:
            self.stateCSVDataset = False
            return
        PathOutput=os.path.dirname(self.lineEdit_csv.currentPath)+'/'

        self.param = {}
        self.param["shapeData"] = self.lineEdit_csv.currentPath
        self.param["coordData"] = self.lineEdit_pshape.currentPath
        self.param["outputDir"] = self.lineEdit_output.directory


        self.starting_time = time.time()
        MFSDAmodule = slicer.modules.mfsda_run
        self.MFSDAThread = slicer.cli.run(MFSDAmodule, None, self.param, wait_for_completion=False)


        self.checkThreadTimer=qt.QTimer()
        self.checkThreadTimer.connect('timeout()', self.onComputationState)
        self.checkThreadTimer.start(1000)

        self.pushButton_run.disconnect('clicked(bool)', self.onCSVFile)
        self.pushButton_run.connect('clicked(bool)', self.onKillComputation)

        return


#
# MFSDALogic
#

class MFSDALogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self, interface):

        self.interface = interface
        self.table = vtk.vtkTable
        self.colorBar = {'Point1': [0, 0, 1, 0], 'Point2': [0.5, 1, 1, 0], 'Point3': [1, 1, 0, 0]}
        #self.input_Data = inputData.inputData()
            
            
    def get(self, objectName):

        """ Functions to recovery the widget in the .ui file
                """
        return slicer.util.findChild(self.interface.widget, objectName)

    def checkExtension(self, filename, extension):
        """ Check if the path given has the right extension"""
        if os.path.splitext(os.path.basename(filename))[1] == extension : 
            return True
        elif os.path.basename(filename) == "" or os.path.basename(filename) == " " :
            return False
        slicer.util.errorDisplay('Wrong extension file, a ' + extension + ' file is needed!' +filename)
        return False

    def onAddGroupForCreationCSVFile(self):
        """Function to add a group of the dictionary
        - Add the paths of all the vtk files found in the directory given 
        of a dictionary which will be used to create the CSV file"""
        directory = self.directoryButton_creationCSVFile.directory
        if directory in self.directoryList:
            index = self.directoryList.index(directory) + 1
            slicer.util.errorDisplay('Path of directory already used for the group ' + str(index))
            return

        # Add the paths of vtk files of the dictionary
        self.logic.addGroupToDictionary(self.dictCSVFile, directory, self.directoryList, self.spinBox_group.value)
        condition = self.logic.checkSeveralMeshInDict(self.dictCSVFile)

        if not condition:
            # Remove the paths of vtk files of the dictionary
            self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)
            return

        # Increment of the number of the group in the spinbox
        self.spinBox_group.blockSignals(True)
        self.spinBox_group.setMaximum(self.spinBox_group.value + 1)
        self.spinBox_group.setValue(self.spinBox_group.value + 1)
        self.spinBox_group.blockSignals(False)

        # Message for the user
        slicer.util.delayDisplay("Group Added")

    def run_script(self, args):
        """
        Run the commandline script for MFSDA.
        """
        """+++++++++++++++++++++++++++++++++++"""
        """Step 1. load dataset """
        
        print("loading data ......")
        print("+++++++Read the surface shape data+++++++")
        
        fh = open(args.shapeData, 'rU')
        
        y_design = []
        nshape = 0
        numpoints = -1
        
        for vtkfilename in fh.readlines():
            print("Reading", vtkfilename)
            vtkfilename=args.shapePath+vtkfilename
            vtkfilename = vtkfilename.rstrip()
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName(vtkfilename)
            reader.Update()
            shapedata = reader.GetOutput()
            shapedatapoints = shapedata.GetPoints()
            
            y_design.append([])
            
            if numpoints == -1:
                numpoints = shapedatapoints.GetNumberOfPoints()
            
            if numpoints != shapedatapoints.GetNumberOfPoints():
                print("WARNING! The number of points is not the same for the shape:", vtkfilename)
            
            for i in range(shapedatapoints.GetNumberOfPoints()):
                p = shapedatapoints.GetPoint(i)
                y_design[nshape].append(p)
            
            nshape += 1

        y_design = np.array(y_design)
        y_design.reshape(nshape, numpoints, 3)

        y_design = np.array(y_design)
        y_design.reshape(nshape, numpoints, 3)
        print("The dimension of shape matrix is " + str(y_design.shape))

        print("+++++++Read the sphere coordinate data+++++++")
        print("Reading", args.coordData)
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(args.coordData)
        reader.Update()
        coordData = reader.GetOutput()
        shapedatapoints = coordData.GetPoints()
        if numpoints != shapedatapoints.GetNumberOfPoints():
            print("WARNING! The template does not have the same number of points as the shapes")
            
        coord_mat = []
        for i in range(shapedatapoints.GetNumberOfPoints()):
            p = shapedatapoints.GetPoint(i)
            coord_mat.append(p)

        coord_mat = np.array(coord_mat)

        print("+++++++Read the design matrix+++++++")
        design_data_file_name = args.covariate
        _ , file_extension = os.path.splitext(design_data_file_name)
            
        delimiter = ' '
        if file_extension == '.csv':
            delimiter=','

        design_data_tmp = np.loadtxt(design_data_file_name, delimiter=delimiter)
        if len(design_data_tmp.shape) == 1:
            design_data = np.reshape(design_data_tmp, (design_data_tmp.shape[0], 1))
        else:
            design_data = design_data_tmp

        # read the covariate type
        var_type_file_name = args.covariateType
        _ , file_extension = os.path.splitext(var_type_file_name)
            
        delimiter = ' '
        if file_extension == '.csv':
            delimiter=','

        var_type = np.loadtxt(var_type_file_name, delimiter=delimiter)

        """+++++++++++++++++++++++++++++++++++"""
        """Step 2. Statistical analysis: including (1) smoothing and (2) hypothesis testing"""
        #print('y_design', y_design, 'y_design', coord_mat, 'design_data', design_data, 'var_type', var_type)
        gpvals, lpvals_fdr, clu_pvals, efit_beta, efity_design, efit_eta = mfsda.run_stats(y_design, coord_mat, design_data, var_type)
            
        """+++++++++++++++++++++++++++++++++++"""
        """Step3. Save all the results"""
            
        if not os.path.exists(args.outputDir):
            os.makedirs(args.outputDir)

        pvalues = {}
        pvalues['Gpvals'] = gpvals.tolist()
        pvalues['clu_pvals'] = clu_pvals.tolist()
        pvalues['Lpvals_fdr'] = lpvals_fdr.tolist()

        with open(os.path.join(args.outputDir,'pvalues.json'), 'w') as outfile:
            json.dump(pvalues, outfile)
            
        efit = {}
        efit['efitBetas'] = efit_beta.tolist()
        efit['efitYdesign'] = efity_design.tolist()
        efit['efitEtas'] = efit_eta.tolist()
        
        with open(os.path.join(args.outputDir,'efit.json'), 'w') as outfile:
            json.dump(efit, outfile)

        # if __name__ == '__main__':
            
    def run_Shape(self, args):

        with open(args.pvalues) as data_file:
            pvalues = json.load(data_file)
            lpvalues = np.array(pvalues['Lpvals_fdr'])

        with open(args.efit) as data_file:
            efit = json.load(data_file)
            efitbetas = np.array(efit['efitBetas'])

        covariates = args.covariates

        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(args.shape)
        reader.Update()
        shapedata = reader.GetOutput()

        pointdata = shapedata.GetPointData()    

        print("Adding pvalues...", lpvalues.shape)

        for j in range(lpvalues.shape[1]):

            arr = vtk.vtkDoubleArray()
            name = 'pvalue_'
            if covariates and j < len(covariates):
                name += covariates[j]
            else:
                name += str(j)

            arr.SetName(name)

            for i in range(lpvalues.shape[0]):            
                arr.InsertNextTuple([lpvalues[i][j]])
            pointdata.AddArray(arr)


        print("Adding betas...", efitbetas.shape)

        for k in range(efitbetas.shape[2]):
            for i in range(efitbetas.shape[0]):        
                arr = vtk.vtkDoubleArray()

                name = 'betavalues_' + str(k) + "_"

                if covariates and i < len(covariates):
                    name += covariates[i]
                else:
                    name += str(i)

                arr.SetName(name)
                
                for j in range(efitbetas.shape[1]):                
                    arr.InsertNextTuple([efitbetas[i][j][k]])
                pointdata.AddArray(arr)


        print("Writing output vtk file...")

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(args.output)
        writer.SetInputData(shapedata)
        writer.Update()


class arguments(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)                

class MFSDATest(ScriptedLoadableModuleTest):

    def SetUp(self):
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        self.SetUp()
        vtk_currentPath='/Users/loicmichoud/Desktop/ficher_test/shapeData.txt'
        template_currentPath='/Users/loicmichoud/Desktop/ficher_test/ALLM_aligned.vtk'
        output_directory='/Users/loicmichoud/Desktop/MySlicerExtensions/output'
        covariate_currentPath='/Users/loicmichoud/Desktop/MFSDA_Python/TEST/covariate.csv'
        covariateType_currentPath='/Users/loicmichoud/Desktop/MFSDA_Python/TEST/covariateType.csv'
        pshape_currentPath='/Users/loicmichoud/Desktop/ficher_test/01_Left_aligned.vtk'
        CovariateNames_currentPath='/Users/loicmichoud/Desktop/MySlicerExtensions/MFSDA/MFSDA/covariate'
        PathOutput=os.path.dirname(vtk_currentPath)+'/'
        args=arguments(coordData=template_currentPath, covariate=covariate_currentPath, covariateType=covariateType_currentPath, outputDir=output_directory, shapeData=vtk_currentPath, shapePath=PathOutput)
        self.run_script(args)
        pvaluesPath=output_directory+'/pvalues.json'
        efitPath=output_directory+'/efit.json'
        pshape=pshape_currentPath
        outputPath=output_directory+'/out.vtk'
        argShapes=arguments(pvalues=pvaluesPath, covariates=CovariateNames_currentPath, shape=pshape_currentPath, efit=efitPath, output=outputPath)
        self.run_Shape(argShapes)
        CSVFile=open(output_directory+'/output.csv', 'w')
        Data=['VTK Files']
        with CSVFile:
            writer = csv.writer(CSVFile)
            writer.writerow(Data)
            writer.writerow([pshape_currentPath])
        CSVFile.close()
        csvFilePath = self.lineEdit_output.directory+'/output.csv'
        slicer.modules.shapepopulationviewer.widgetRepresentation().loadCSVFile(csvFilePath)
        slicer.util.selectModule(slicer.modules.shapepopulationviewer)

    def run_script(self, args):
        """
        Run the commandline script for MFSDA.
        """
        """+++++++++++++++++++++++++++++++++++"""
        """Step 1. load dataset """
        
        print("loading data ......")
        print("+++++++Read the surface shape data+++++++")
        
        fh = open(args.shapeData, 'rU')
        
        y_design = []
        nshape = 0
        numpoints = -1
        
        for vtkfilename in fh.readlines():
            print("Reading", vtkfilename)
            vtkfilename=args.shapePath+vtkfilename
            vtkfilename = vtkfilename.rstrip()
            reader = vtk.vtkPolyDataReader()
            reader.SetFileName(vtkfilename)
            reader.Update()
            shapedata = reader.GetOutput()
            shapedatapoints = shapedata.GetPoints()
            
            y_design.append([])
            
            if numpoints == -1:
                numpoints = shapedatapoints.GetNumberOfPoints()
            
            if numpoints != shapedatapoints.GetNumberOfPoints():
                print("WARNING! The number of points is not the same for the shape:", vtkfilename)
            
            for i in range(shapedatapoints.GetNumberOfPoints()):
                p = shapedatapoints.GetPoint(i)
                y_design[nshape].append(p)
            
            nshape += 1

        y_design = np.array(y_design)
        y_design.reshape(nshape, numpoints, 3)

        y_design = np.array(y_design)
        y_design.reshape(nshape, numpoints, 3)
        print("The dimension of shape matrix is " + str(y_design.shape))

        print("+++++++Read the sphere coordinate data+++++++")
        print("Reading", args.coordData)
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(args.coordData)
        reader.Update()
        coordData = reader.GetOutput()
        shapedatapoints = coordData.GetPoints()
        if numpoints != shapedatapoints.GetNumberOfPoints():
            print("WARNING! The template does not have the same number of points as the shapes")
            
        coord_mat = []
        for i in range(shapedatapoints.GetNumberOfPoints()):
            p = shapedatapoints.GetPoint(i)
            coord_mat.append(p)

        coord_mat = np.array(coord_mat)

        print("+++++++Read the design matrix+++++++")
        design_data_file_name = args.covariate
        _ , file_extension = os.path.splitext(design_data_file_name)
            
        delimiter = ' '
        if file_extension == '.csv':
            delimiter=','

        design_data_tmp = np.loadtxt(design_data_file_name, delimiter=delimiter)
        if len(design_data_tmp.shape) == 1:
            design_data = np.reshape(design_data_tmp, (design_data_tmp.shape[0], 1))
        else:
            design_data = design_data_tmp
    

        # read the covariate type
        var_type_file_name = args.covariateType
        _ , file_extension = os.path.splitext(var_type_file_name)
            
        delimiter = ' '
        if file_extension == '.csv':
            delimiter=','

        var_type = np.loadtxt(var_type_file_name, delimiter=delimiter)

        """+++++++++++++++++++++++++++++++++++"""
        """Step 2. Statistical analysis: including (1) smoothing and (2) hypothesis testing"""
#        print('y_design', y_design, 'y_design', coord_mat, 'design_data', design_data, 'var_type', var_type)
        gpvals, lpvals_fdr, clu_pvals, efit_beta, efity_design, efit_eta = mfsda.run_stats(y_design, coord_mat, design_data, var_type)
            
        """+++++++++++++++++++++++++++++++++++"""
        """Step3. Save all the results"""
            
        if not os.path.exists(args.outputDir):
            os.makedirs(args.outputDir)

        pvalues = {}
        pvalues['Gpvals'] = gpvals.tolist()
        pvalues['clu_pvals'] = clu_pvals.tolist()
        pvalues['Lpvals_fdr'] = lpvals_fdr.tolist()

        with open(os.path.join(args.outputDir,'pvalues.json'), 'w') as outfile:
            json.dump(pvalues, outfile)
            
        efit = {}
        efit['efitBetas'] = efit_beta.tolist()
        efit['efitYdesign'] = efity_design.tolist()
        efit['efitEtas'] = efit_eta.tolist()
        
        with open(os.path.join(args.outputDir,'efit.json'), 'w') as outfile:
            json.dump(efit, outfile)

        # if __name__ == '__main__':
            
    def run_Shape(self, args):

        with open(args.pvalues) as data_file:
            pvalues = json.load(data_file)
            lpvalues = np.array(pvalues['Lpvals_fdr'])

        with open(args.efit) as data_file:
            efit = json.load(data_file)
            efitbetas = np.array(efit['efitBetas'])

        covariates = args.covariates

        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(args.shape)
        reader.Update()
        shapedata = reader.GetOutput()

        pointdata = shapedata.GetPointData()    

        print("Adding pvalues...", lpvalues.shape)

        for j in range(lpvalues.shape[1]):

            arr = vtk.vtkDoubleArray()
            name = 'pvalue_'
            if covariates and j < len(covariates):
                name += covariates[j]
            else:
                name += str(j)

            arr.SetName(name)

            for i in range(lpvalues.shape[0]):            
                arr.InsertNextTuple([lpvalues[i][j]])
            pointdata.AddArray(arr)


        print("Adding betas...", efitbetas.shape)

        for k in range(efitbetas.shape[2]):
            for i in range(efitbetas.shape[0]):        
                arr = vtk.vtkDoubleArray()

                name = 'betavalues_' + str(k) + "_"

                if covariates and i < len(covariates):
                    name += covariates[i]
                else:
                    name += str(i)

                arr.SetName(name)
                
                for j in range(efitbetas.shape[1]):                
                    arr.InsertNextTuple([efitbetas[i][j][k]])
                pointdata.AddArray(arr)


        print("Writing output vtk file...")

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(args.output)
        writer.SetInputData(shapedata)
        writer.Update()


    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
