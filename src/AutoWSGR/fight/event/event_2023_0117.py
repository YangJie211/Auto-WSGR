
import os

from AutoWSGR.controller.run_timer import Timer
from AutoWSGR.constants.data_roots import MAP_ROOT
from AutoWSGR.fight.battle import BattleInfo, BattlePlan
from AutoWSGR.fight.common import start_march
from AutoWSGR.fight.normal_fight import NormalFightInfo, NormalFightPlan
from AutoWSGR.game.game_operation import MoveTeam, QuickRepair
from AutoWSGR.utils.math_functions import CalcDis

from AutoWSGR.fight.event.event import PatrollingEvent


MAP_POSITIONS = [None, (100, 200), (500, 450), (520, 220), (350, 330), (600, 100), (700, 400)]


class EventFightPlan20230117(PatrollingEvent, NormalFightPlan):
    
    def __init__(self, timer: Timer, plan_path, fleet_id=None, event="20230117"):
        self.event_name = event
        NormalFightPlan.__init__(self, timer, plan_path, fleet_id=fleet_id)
        PatrollingEvent.__init__(self, timer, event, MAP_POSITIONS)
        
    def load_fight_info(self):
        # 地图文件位置: AutoWSGR/data/map/event/{event_name}
        # event_name 通常采用活动开始日期
        self.Info = EventFightInfo20230117(self.timer, self.chapter, self.map)
        self.Info.load_point_positions(os.path.join(MAP_ROOT, 'event', self.event_name))
     
    def change_fight_map(self, chapter_id, map_id):
        """对 normal_fight 的 change_fight_map 的重写
        """
        self.enter_map(chapter_id, map_id)
        while(self.timer.image_exist(self.common_image['little_monster']) == False): # 找到小怪物图标,点击下方进入主力决战
            while(self.timer.wait_images_position(self.common_image['monster'], timeout=1) is None):
                self.random_walk()
            if(self.timer.image_exist(self.common_image['little_monster'])):
                break
            ret = self.timer.wait_images_position(self.common_image['monster'])
            self.timer.Android.click(*ret)
        
        ret = self.get_close(self.common_image['little_monster'][0])
        self.timer.Android.click(ret[0], ret[1] + 60)
        assert(self.timer.wait_image(self.event_image[1]))
    
    
class EventFightInfo20230117(PatrollingEvent, NormalFightInfo):
    
    def __init__(self, timer: Timer, chapter_id, map_id, event="20230117") -> None:
        NormalFightInfo.__init__(self, timer, chapter_id, map_id)
        PatrollingEvent.__init__(self, timer, event, MAP_POSITIONS)
        self.map_image = self.event_image[1]
        self.end_page = 'unknown_page'
        self.state2image["map_page"] = [self.map_image, 5]
        

class EventFightPlan20230117_2(PatrollingEvent, BattlePlan):
    def __init__(self, timer: Timer, plan_path, fleet_id=None, event="20230117"):
        self.event_name = event
        self.fleet_id = fleet_id
        BattlePlan.__init__(self, timer, plan_path)
        PatrollingEvent.__init__(self, timer, event, MAP_POSITIONS)

    def _enter_fight(self, same_work=False):
        self.go_map_page()
        self.enter_map(self.chapter, self.map)
        assert(self.timer.wait_image(self.event_image[2]) is not False)
        self.find(self.enemy_image[self.target])
        ret = self.get_close(self.enemy_image[self.target])
        self.timer.Android.click(*ret)
        assert(self.timer.wait_image(self.event_image[4]) != False)
        self.timer.Android.click(900, 500)
        self.timer.wait_pages('fight_prepare_page', after_wait=.15)
        MoveTeam(self.timer, self.fleet_id)
        QuickRepair(self.timer, self.repair_mode)
        return start_march(self.timer)
    
    
class EventFightInfo20230117_2(PatrollingEvent, BattleInfo):
    def __init__(self, timer: Timer, chapter, map, event="20230117") -> None:
        BattleInfo.__init__(self, timer, chapter, map)
        PatrollingEvent.__init__(self, timer, event, MAP_POSITIONS)
        self.end_page = 'unknown_page'
        self.state2image["battle_page"] = [self.event_image[2], 5]
