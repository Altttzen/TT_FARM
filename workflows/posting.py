from actions.humanize import sleep_jitter

class PostingWorkflow:
    def __init__(self, cfg: dict, device, limits):
        self.cfg = cfg
        self.device = device
        self.limits = limits

    def tick(self):
        # ВНИМАНИЕ: Реальный постинг зависит от UI TikTok и галереи.
        # Этот модуль — каркас:
        # - детект кнопки "+"
        # - выбор видео из галереи
        # - next -> caption -> post
        #
        # Делается так же, как лайк: через шаблоны кнопок.
        sleep_jitter(0.2, 0.1)
        return
