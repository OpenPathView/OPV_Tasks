from opv_tasks.task import Task
from opv_api_client import ressources
import cv2
from path import Path


class DetectholeTask(Task):
    """
        Find panorama assembly error
        Input format :
            opv-task detecthole '{"id_panorama": ID_PANORAMA, "id_malette": ID_MALETTE }'
    """
    TASK_NAME = "detecthole"
    requiredArgsKeys = ["id_malette", "id_panorama"]

    MIN_AREA = 3
    MAX_BASE_HOLE = 1250
    THRESHOLD = 100 

    def detectHole(self):
        self.logger.info("Hole test")
        # Convert each black pixel in white and other pixel in black
        panorama_img = cv2.threshold(self.panorama_img, 0, 255, cv2.THRESH_BINARY_INV)[1]
        # Find contour around white shape
        contours = cv2.findContours(panorama_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        hole = []

        for contour in contours:
            area = cv2.contourArea(contour)
            # To avoid artefact or natural black pixels
            if area > 10**self.MIN_AREA:
                hole.append(contour)
        
        if len(hole) > 1:
            self.logger.info("Panorama has too much hole ({} hole)".format(len(hole)-1))
            return 1
        else:
            # Check if an hole is connected to the base hole 
            height = cv2.boundingRect(hole[0])[3]
            if height > self.MAX_BASE_HOLE:
                self.logger.info("Panorama has an error on base hole ({}px)".format(height))
                return 1
            else:
                return 0

    def runWithExceptions(self, options={}):
        self.checkArgs(options)
        self.pano = self._client_requestor.make(ressources.Panorama, options["id_panorama"], options["id_malette"])

        with self._opv_directory_manager.Open(self.pano.equirectangular_path) as (name, dir_path):
            self.pano_path = Path(dir_path) / "panorama.jpg"
            self.panorama_img = cv2.imread(self.pano_path)
            # Convert panorama in a one channel image
            self.panorama_img = cv2.cvtColor(self.panorama_img, cv2.COLOR_BGR2GRAY)

            error = self.detectHole()

        if error:
            self.logger.info("This panorama has problem(s)")
            self.pano.is_blur = True
        else: 
            self.logger.info("This panorama seem good")
            self.pano.is_blur = False

        self.pano.save()

        return self.pano.id
