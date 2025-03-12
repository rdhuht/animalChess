import pygame
import sys
from enum import Enum
from utils import load_svg, get_piece_image_path

# 初始化Pygame
pygame.init()

# 定义棋子类型
class PieceType(Enum):
    ELEPHANT = 8
    LION = 7
    TIGER = 6
    LEOPARD = 5
    WOLF = 4
    DOG = 3
    CAT = 2
    RAT = 1

# 定义棋子类
class Piece:
    def __init__(self, piece_type, player, pos):
        self.type = piece_type
        self.player = player  # 'red' or 'blue'
        self.pos = pos  # (row, col)
        self.selected = False
        
    def can_move(self, target_pos, board):
        row, col = self.pos
        target_row, target_col = target_pos
        
        # 狮虎跳河规则
        if self.type in [PieceType.LION, PieceType.TIGER]:
            # 检查是否是横向或纵向跳跃
            if (row == target_row and abs(col - target_col) == 3) or \
               (col == target_col and abs(row - target_row) == 4):
                # 检查是否跨河
                if self._is_valid_jump(row, col, target_row, target_col, board):
                    return True
        
        # 基本移动规则：只能上下左右移动一格
        if abs(row - target_row) + abs(col - target_col) != 1:
            return False
            
        # 检查目标位置是否有己方棋子
        if board[target_row][target_col] is not None:
            if board[target_row][target_col].player == self.player:
                return False
                
        # 特殊规则：河流判定
        if self._is_river(target_row, target_col):
            if self.type != PieceType.RAT:
                return False
                
        # 特殊规则：兽穴判定
        if self._is_den(target_row, target_col, self.player):
            return False
            
        return True

    def _is_valid_jump(self, row, col, target_row, target_col, board):
        # 检查是否是有效的跳跃（没有老鼠阻挡）
        if row == target_row:  # 横向跳跃
            start_col = min(col, target_col) + 1
            end_col = max(col, target_col)
            for c in range(start_col, end_col):
                if board[row][c] is not None and board[row][c].type == PieceType.RAT:
                    return False
        else:  # 纵向跳跃
            start_row = min(row, target_row) + 1
            end_row = max(row, target_row)
            for r in range(start_row, end_row):
                if board[r][col] is not None and board[r][col].type == PieceType.RAT:
                    return False
        return True
        
    def can_capture(self, target_piece, board):
        # 检查是否在对方陷阱中
        target_row, target_col = target_piece.pos
        if target_piece._is_trap(target_row, target_col, self.player):
            return True  # 在对方陷阱中的棋子可以被任意棋子吃掉，因为其战斗力变为0
        
        # 检查自己是否在对方陷阱中
        row, col = self.pos
        if self._is_trap(row, col, target_piece.player):
            return False  # 在对方陷阱中的棋子战斗力为0，无法吃掉其他棋子
        
        # 老鼠可以吃大象
        if self.type == PieceType.RAT and target_piece.type == PieceType.ELEPHANT:
            return True
        # 大象不能吃老鼠
        if self.type == PieceType.ELEPHANT and target_piece.type == PieceType.RAT:
            return False
        # 其他情况下，大的可以吃小的
        return self.type.value >= target_piece.type.value
        
    def _is_river(self, row, col):
        return (3 <= row <= 5) and (col in [1, 2, 4, 5])
        
    def _is_den(self, row, col, player):
        if player == 'red':
            return row == 8 and col == 3
        else:
            return row == 0 and col == 3
        
    def _is_trap(self, row, col, player):
        if player == 'red':
            return (row == 8 and col == 2) or \
                   (row == 8 and col == 4) or \
                   (row == 7 and col == 3)
        else:
            return (row == 0 and col == 2) or \
                   (row == 0 and col == 4) or \
                   (row == 1 and col == 3)

class DouShouQi:
    def __init__(self):
        # 设置窗口大小
        self.WINDOW_SIZE = (800, 900)
        self.BOARD_SIZE = (700, 800)  # 棋盘大小
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption('斗兽棋')
        
        # 初始化字体
        self.font = pygame.font.SysFont('SimHei', 30)
        self.turn_font = pygame.font.SysFont('SimHei', 40)  # 回合提示字体
        self.winner_font = pygame.font.SysFont('SimHei', 60)  # 获胜提示字体
        
        # 颜色定义
        self.BACKGROUND_COLOR = (227, 205, 168)  # 竹简色 #E3CDA8
        self.GRID_COLOR = (139, 90, 43)    # 深木色 #8B5A2B
        self.RED_COLOR = (178, 34, 34)     # 深红色 #B22222
        self.BLUE_COLOR = (30, 58, 95)     # 深蓝色 #1E3A5F
        self.RIVER_COLOR = (118, 195, 229)  # 柔和蓝色 #76C3E5
        self.TRAP_COLOR = (139, 0, 0)      # 暗红色 #8B0000
        self.DEN_COLOR = (215, 184, 153)   # 浅木色 #D7B899
        self.TEXT_COLOR = (255, 255, 255)  # 白色 #FFFFFF
        
        # 棋盘格子大小
        self.CELL_SIZE = min(self.BOARD_SIZE[0] // 7, self.BOARD_SIZE[1] // 9)
        self.LINE_WIDTH = max(2, self.CELL_SIZE // 20)  # 根据格子大小调整线条粗细
        
        # 加载棋子图片
        self.load_piece_images()
        
        # 初始化棋盘状态
        self.board = [[None for _ in range(7)] for _ in range(9)]
        self.selected_piece = None
        self.current_player = 'red'  # 红方先手
        self.dragging = False
        self.drag_pos = None
        self.winner = None
        
        # 初始化日志文件
        self.init_log_file()
        
        # 初始化棋子位置
        self.init_pieces()

    def init_log_file(self):
        self.log_file = open('game_log.txt', 'w', encoding='utf-8')
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_file.write('斗兽棋对战记录\n')
        self.log_file.write('对局开始时间：' + current_time + '\n')
        self.log_file.write('=' * 30 + '\n')
        self.log_file.flush()

    def log_move(self, piece, old_pos, new_pos, captured_piece=None):
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        player_name = '红方' if piece.player == 'red' else '蓝方'
        piece_name = {
            PieceType.ELEPHANT: '象',
            PieceType.LION: '狮',
            PieceType.TIGER: '虎',
            PieceType.LEOPARD: '豹',
            PieceType.WOLF: '狼',
            PieceType.DOG: '狗',
            PieceType.CAT: '猫',
            PieceType.RAT: '鼠'
        }[piece.type]

        old_row, old_col = old_pos
        new_row, new_col = new_pos
        move_str = f'[{current_time}] {player_name}{piece_name}从({old_row},{old_col})移动到({new_row},{new_col})'

        if captured_piece:
            captured_name = {
                PieceType.ELEPHANT: '象',
                PieceType.LION: '狮',
                PieceType.TIGER: '虎',
                PieceType.LEOPARD: '豹',
                PieceType.WOLF: '狼',
                PieceType.DOG: '狗',
                PieceType.CAT: '猫',
                PieceType.RAT: '鼠'
            }[captured_piece.type]
            move_str += f'，吃掉了对方的{captured_name}'

        self.log_file.write(move_str + '\n')
        self.log_remaining_pieces()
        self.log_file.flush()

    def log_remaining_pieces(self):
        red_pieces = []
        blue_pieces = []
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    piece_name = {
                        PieceType.ELEPHANT: '象',
                        PieceType.LION: '狮',
                        PieceType.TIGER: '虎',
                        PieceType.LEOPARD: '豹',
                        PieceType.WOLF: '狼',
                        PieceType.DOG: '狗',
                        PieceType.CAT: '猫',
                        PieceType.RAT: '鼠'
                    }[piece.type]
                    if piece.player == 'red':
                        red_pieces.append(piece_name)
                    else:
                        blue_pieces.append(piece_name)

        self.log_file.write(f'红方剩余棋子：{",".join(red_pieces)}\n')
        self.log_file.write(f'蓝方剩余棋子：{",".join(blue_pieces)}\n')
        self.log_file.write('-' * 30 + '\n')

    def check_win(self):
        # 检查是否有一方进入对方兽穴
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    # 检查是否进入对方兽穴
                    if (piece.player == 'red' and row == 0 and col == 3) or \
                       (piece.player == 'blue' and row == 8 and col == 3):
                        return piece.player

        # 检查是否有一方的棋子全部被吃掉
        red_pieces = blue_pieces = 0
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    if piece.player == 'red':
                        red_pieces += 1
                    else:
                        blue_pieces += 1

        if red_pieces == 0:
            return 'blue'
        if blue_pieces == 0:
            return 'red'

        return None

    def draw_board(self):
        # 绘制棋盘背景
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # 计算棋盘的起始位置（居中）
        start_x = (self.WINDOW_SIZE[0] - 7 * self.CELL_SIZE) // 2
        start_y = (self.WINDOW_SIZE[1] - 9 * self.CELL_SIZE) // 2
        
        # 绘制棋盘边框
        border_color = self.RED_COLOR if self.current_player == 'red' else self.BLUE_COLOR
        pygame.draw.rect(self.screen, border_color,
                       (start_x - self.LINE_WIDTH, start_y - self.LINE_WIDTH,
                        7 * self.CELL_SIZE + 2 * self.LINE_WIDTH,
                        9 * self.CELL_SIZE + 2 * self.LINE_WIDTH),
                       self.LINE_WIDTH)
        

        
        # 计算棋盘的起始位置（居中）
        start_x = (self.WINDOW_SIZE[0] - 7 * self.CELL_SIZE) // 2
        start_y = (self.WINDOW_SIZE[1] - 9 * self.CELL_SIZE) // 2
        
        # 绘制特殊区域
        # 河流
        for row in range(3, 6):
            for col in [1, 2, 4, 5]:
                pygame.draw.rect(self.screen, self.RIVER_COLOR,
                               (start_x + col * self.CELL_SIZE,
                                start_y + row * self.CELL_SIZE,
                                self.CELL_SIZE, self.CELL_SIZE))
        
        # 陷阱
        trap_positions = [(0, 2), (0, 4), (1, 3), (8, 2), (8, 4), (7, 3)]
        for row, col in trap_positions:
            # 绘制陷阱底色
            pygame.draw.rect(self.screen, self.TRAP_COLOR,
                           (start_x + col * self.CELL_SIZE,
                            start_y + row * self.CELL_SIZE,
                            self.CELL_SIZE, self.CELL_SIZE))
            # 绘制十字形图案
            center_x = start_x + col * self.CELL_SIZE + self.CELL_SIZE // 2
            center_y = start_y + row * self.CELL_SIZE + self.CELL_SIZE // 2
            line_length = self.CELL_SIZE // 3
            # 绘制横线
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (center_x - line_length, center_y),
                           (center_x + line_length, center_y),
                           2)
            # 绘制竖线
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (center_x, center_y - line_length),
                           (center_x, center_y + line_length),
                           2)
        
        # 兽穴
        den_positions = [(0, 3), (8, 3)]
        for row, col in den_positions:
            center_x = start_x + col * self.CELL_SIZE + self.CELL_SIZE // 2
            center_y = start_y + row * self.CELL_SIZE + self.CELL_SIZE // 2
            # 绘制圆形底色
            pygame.draw.circle(self.screen, self.DEN_COLOR,
                             (center_x, center_y),
                             self.CELL_SIZE // 2)
            # 绘制内部装饰圆环
            pygame.draw.circle(self.screen, self.GRID_COLOR,
                             (center_x, center_y),
                             self.CELL_SIZE // 3,
                             2)
            # 绘制中心点
            pygame.draw.circle(self.screen, self.GRID_COLOR,
                             (center_x, center_y),
                             self.CELL_SIZE // 8)
        
        # 绘制横线
        for i in range(10):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (start_x, start_y + i * self.CELL_SIZE),
                           (start_x + 7 * self.CELL_SIZE, start_y + i * self.CELL_SIZE))
        
        # 绘制竖线
        for i in range(8):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                           (start_x + i * self.CELL_SIZE, start_y),
                           (start_x + i * self.CELL_SIZE, start_y + 9 * self.CELL_SIZE))
        
        # 绘制棋子
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    color = self.RED_COLOR if piece.player == 'red' else self.BLUE_COLOR
                    center_x = start_x + col * self.CELL_SIZE + self.CELL_SIZE // 2
                    center_y = start_y + row * self.CELL_SIZE + self.CELL_SIZE // 2
                    
                    # 绘制棋子圆形
                    pygame.draw.circle(self.screen, color,
                                     (center_x, center_y),
                                     self.CELL_SIZE // 3)
                    
                    # 绘制选中效果
                    if piece.selected or (self.dragging and piece == self.selected_piece):
                        pygame.draw.circle(self.screen, (255, 255, 0),
                                         (center_x, center_y),
                                         self.CELL_SIZE // 3, 2)
                    
                    # 绘制棋子图片
                    image = self.piece_images.get((piece.type, piece.player))
                    if image:
                        # 计算图片位置（居中显示）
                        image_rect = image.get_rect()
                        image_rect.center = (center_x, center_y)
                        self.screen.blit(image, image_rect)
                    else:
                        # 如果没有找到图片，使用文字作为后备显示
                        piece_name = {
                            PieceType.ELEPHANT: '象',
                            PieceType.LION: '狮',
                            PieceType.TIGER: '虎',
                            PieceType.LEOPARD: '豹',
                            PieceType.WOLF: '狼',
                            PieceType.DOG: '狗',
                            PieceType.CAT: '猫',
                            PieceType.RAT: '鼠'
                        }[piece.type]
                        text = self.font.render(piece_name, True, self.TEXT_COLOR)
                        text_rect = text.get_rect(center=(center_x, center_y))
                        self.screen.blit(text, text_rect)
    
    def get_board_position(self, mouse_pos):
        # 计算棋盘的起始位置
        start_x = (self.WINDOW_SIZE[0] - 7 * self.CELL_SIZE) // 2
        start_y = (self.WINDOW_SIZE[1] - 9 * self.CELL_SIZE) // 2
        
        # 计算鼠标位置对应的棋盘格子
        x, y = mouse_pos
        col = (x - start_x) // self.CELL_SIZE
        row = (y - start_y) // self.CELL_SIZE
        
        # 检查是否在棋盘范围内
        if 0 <= row < 9 and 0 <= col < 7:
            return row, col
        return None
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                

                
                # 处理鼠标事件
                if not self.winner:  # 只有在游戏未结束时才处理移动
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = self.get_board_position(event.pos)
                        if pos:
                            row, col = pos
                            piece = self.board[row][col]
                            if piece and piece.player == self.current_player:
                                self.selected_piece = piece
                                self.dragging = True
                                self.drag_pos = event.pos
                
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.drag_pos = event.pos
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.dragging:
                        pos = self.get_board_position(event.pos)
                        if pos and self.selected_piece:
                            row, col = pos
                            old_row, old_col = self.selected_piece.pos
                            
                            # 检查移动是否合法
                            if self.selected_piece.can_move(pos, self.board):

                                
                                # 如果目标位置有对方棋子
                                target_piece = self.board[row][col]
                                old_pos = self.selected_piece.pos
                                
                                if target_piece:
                                    if self.selected_piece.can_capture(target_piece, self.board):
                                        # 吃掉对方棋子
                                        self.board[row][col] = self.selected_piece
                                        self.board[old_row][old_col] = None
                                        self.selected_piece.pos = pos
                                        self.log_move(self.selected_piece, old_pos, pos, target_piece)

                                        self.current_player = 'blue' if self.current_player == 'red' else 'red'
                                else:
                                    # 移动到空位置
                                    self.board[row][col] = self.selected_piece
                                    self.board[old_row][old_col] = None
                                    self.selected_piece.pos = pos
                                    self.log_move(self.selected_piece, old_pos, pos)

                                    self.current_player = 'blue' if self.current_player == 'red' else 'red'
                                
                                # 检查胜利条件
                                winner = self.check_win()
                                if winner:
                                    self.winner = winner
                                    winner_text = '红方胜利！' if winner == 'red' else '蓝方胜利！'
                                    self.log_file.write('\n' + winner_text + '\n')
                        
                        self.dragging = False
                        self.selected_piece = None
                        self.drag_pos = None
            
            # 绘制游戏界面
            self.draw_board()
            
            # 如果有获胜方，显示获胜信息
            if self.winner:
                winner_text = '红方胜利！' if self.winner == 'red' else '蓝方胜利！'
                winner_surface = self.winner_font.render(winner_text, True,
                                                       self.RED_COLOR if self.winner == 'red' else self.BLUE_COLOR)
                text_rect = winner_surface.get_rect(center=(self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2))
                self.screen.blit(winner_surface, text_rect)
            
            pygame.display.flip()
    
    def save_board_state(self):
        # 保存当前棋盘状态
        state = []
        for row in range(9):
            for col in range(7):
                piece = self.board[row][col]
                if piece:
                    state.append({
                        'type': piece.type,
                        'player': piece.player,
                        'pos': piece.pos
                    })
        return {
            'board': state,
            'current_player': self.current_player
        }
    
    def restore_board_state(self, state):
        # 恢复棋盘状态
        self.board = [[None for _ in range(7)] for _ in range(9)]
        for piece_data in state['board']:
            piece = Piece(piece_data['type'], piece_data['player'], piece_data['pos'])
            row, col = piece_data['pos']
            self.board[row][col] = piece
        self.current_player = state['current_player']
    
    def undo_move(self):
        if self.move_history and self.undo_chances[self.current_player] > 0:
            previous_state = self.move_history.pop()
            self.restore_board_state(previous_state)
            self.undo_chances[self.current_player] -= 1
            self.log_file.write(f'{"红方" if self.current_player == "red" else "蓝方"}进行了悔棋，剩余{self.undo_chances[self.current_player]}次机会\n')
            self.log_file.flush()

    def load_piece_images(self):
        # 加载所有棋子的SVG图片
        piece_size = (self.CELL_SIZE // 2, self.CELL_SIZE // 2)  # 棋子图片大小为格子的一半
        for piece_type in PieceType:
            for player in ['red', 'blue']:
                try:
                    image_path = get_piece_image_path(piece_type, player)
                    image = load_svg(image_path, piece_size)
                    self.piece_images[(piece_type, player)] = image
                except FileNotFoundError:
                    print(f"警告：找不到图片文件 {image_path}")
                    self.piece_images[(piece_type, player)] = None

    def init_pieces(self):
        # 初始化蓝方棋子
        self.board[0][0] = Piece(PieceType.LION, 'blue', (0, 0))
        self.board[0][6] = Piece(PieceType.TIGER, 'blue', (0, 6))
        self.board[1][1] = Piece(PieceType.DOG, 'blue', (1, 1))
        self.board[1][5] = Piece(PieceType.CAT, 'blue', (1, 5))
        self.board[2][0] = Piece(PieceType.RAT, 'blue', (2, 0))
        self.board[2][2] = Piece(PieceType.LEOPARD, 'blue', (2, 2))
        self.board[2][4] = Piece(PieceType.WOLF, 'blue', (2, 4))
        self.board[2][6] = Piece(PieceType.ELEPHANT, 'blue', (2, 6))

        # 初始化红方棋子
        self.board[8][6] = Piece(PieceType.LION, 'red', (8, 6))
        self.board[8][0] = Piece(PieceType.TIGER, 'red', (8, 0))
        self.board[7][5] = Piece(PieceType.DOG, 'red', (7, 5))
        self.board[7][1] = Piece(PieceType.CAT, 'red', (7, 1))
        self.board[6][6] = Piece(PieceType.RAT, 'red', (6, 6))
        self.board[6][4] = Piece(PieceType.LEOPARD, 'red', (6, 4))
        self.board[6][2] = Piece(PieceType.WOLF, 'red', (6, 2))
        self.board[6][0] = Piece(PieceType.ELEPHANT, 'red', (6, 0))

if __name__ == '__main__':
    game = DouShouQi()
    game.run()