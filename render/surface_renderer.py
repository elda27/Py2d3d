import vtk
import numpy as np
from typing import Tuple, Union
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy
import vtk_util
import math

PolyDataLike = Union[vtk.vtkPolyData, Tuple[np.ndarray, np.ndarray]]


class SurfaceRenderer:
    renderer = None

    def __init__(self, offscreen=True):
        cls = SurfaceRenderer
        if cls.renderer is None:
            cls.renderer = vtk.vtkRenderer()
            self.renderer = cls.renderer
        else:
            self.renderer = cls.renderer

        self.camera = vtk.vtkCamera()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetUseOffScreenBuffers(offscreen)
        self.render_window.AddRenderer(self.renderer)

        self.window_to_image_filter = vtk.vtkWindowToImageFilter()

        self.actors = []

    def set_camera_parameter(self, geometry):
        vtk_extrinsic = vtk_util.convert_numpy_matrix4x4(geometry.extrinsic)
        self.camera.SetModelTransformMatrix(vtk_extrinsic)

        self.camera.SetPosition(0, 0, 0)
        self.camera.SetFocalPoint(0, 0, -1)
        self.camera.SetClippingRange(100, geometry.SDD)

        detector_size = (np.array(geometry.image_size) *
                         np.array(geometry.pixel_spacing))

        rad_angle = math.atan2(detector_size[1] / 2, geometry.SDD)
        self.camera.SetViewAngle(2 * rad_angle * 180 / math.pi)

    def setup_render(self):
        for actor in self.actors:
            self.renderer.RemoveActor(actor)

        self.actors = []
        self.renderer.SetActiveCamera(self.camera)
        self.renderer.SetBackground(0.0, 0.0, 0.0)

    def render(self, poly_data: PolyDataLike, pose=np.zeros(6)) -> None:
        if isinstance(poly_data, tuple):
            poly_data = self.convert_ply2poly_data(*poly_data)

        actor = None
        if (not isinstance(poly_data, vtk.vtkActor) and
                not issubclass(type(poly_data), vtk.vtkActor)):
            actor = self.setup_actor(poly_data)
        else:
            actor = poly_data

        self.actors.append(actor)
        self.renderer.AddActor(actor)

    def flush(self):
        self.render_window.Render()

    def capture(self):
        self.window_to_image_filter.SetInput(self.render_window)
        self.window_to_image_filter.SetMagnification(
            self.image_size[0] / self.render_window.GetSize()[0]
        )
        self.window_to_image_filter.SetInputBufferTypeToRGB()
        self.window_to_image_filter.ReadFrontBufferOff()
        self.window_to_image_filter.Update()

        vtk_image = self.window_to_image_filter.GetOutput()
        rows, cols, _ = vtk_image.GetDimensions()
        vtk_pointer = vtk_image.GetPointData().GetScalars()
        a = vtk_to_numpy(vtk_pointer)
        if a.ndim == 2:
            return None
        a = a.reshape(rows, cols, -1)
        return a

    def setup_actor(self, poly_obj):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_obj)
        mapper.Update()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        return actor

    def convert_ply2poly_data(self, vertices, faces):
        # setup points
        if not isinstance(faces, vtk.vtkPoints):
            vtkArray = numpy_to_vtk(vertices, deep=1)
            points = vtk.vtkPoints()
            points.SetData(vtkArray)
        else:
            points = vertices

        # setup traiangles
        if not isinstance(faces, vtk.vtkCellArray):
            triangles = vtk.vtkCellArray()

            for i in range(len(faces)):
                # create a triangle on the three points in the polydata
                triangle = vtk.vtkTriangle()

                triangle.GetPointIds().SetId(0, faces[i, 0])
                triangle.GetPointIds().SetId(1, faces[i, 1])
                triangle.GetPointIds().SetId(2, faces[i, 2])

                # add the triangle to the list of triangles (in this case there is only 1)
                triangles.InsertNextCell(triangle)
        else:
            triangles = faces

        # create a polydata object
        vkt_poly_data = vtk.vtkPolyData()

        # add the geometry and topology to the polydata
        vkt_poly_data.SetPoints(points)
        vkt_poly_data.SetPolys(triangles)

        return vkt_poly_data
