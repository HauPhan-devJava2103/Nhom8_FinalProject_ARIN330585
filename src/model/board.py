from csv import reader
from dataclasses import dataclass, replace
from collections import defaultdict
from typing import Iterator, List, Tuple
from .move import Move
from .vehicle import Vehicle

def csv_to_matrix(file_path: str) -> List[List[int]]:
    with open(file_path, "r") as csv_file:
        csv_reader = reader(csv_file)
        matrix = [[int(tile) for tile in line] for line in csv_reader]
        return matrix
    
@dataclass(frozen=True)
class Board:
    width: int = 0
    vehicles: Tuple[Vehicle, ...] = ()

    def move_vehicle(self, move: Move) -> "Board":
        new_list = list(self.vehicles)
        new_list[move.vehicle_index] = new_list[move.vehicle_index].move(move)
        return replace(self, vehicles=tuple(new_list))

    @staticmethod
    def from_matrix(matrix: List[List[int]]) -> "Board":
        '''Chuyển đổi Board số thành Board chứa các Vehicle'''
        if len(matrix) < 6 or len(matrix) != len(matrix[0]):
            raise Exception(
                "Wrong shape for matrix. Matrices should be square and have at least 6 rows and columns"  # noqa: E501
            )
        else:
            # Gom tất cả ô thành nhóm theo vehicle_id
            symbol_dict = defaultdict(list)

            for r, row in enumerate(matrix):
                for c, value in enumerate(row):
                    symbol_dict[value].append((r,c))


            # Tạo các Vehicle từ nhóm tọa độ

            vehicles = []
            for vehicle_id, tiles in sorted(symbol_dict.items()):
                # Trường hợp -1 -> ô trống bỏ qua
                if vehicle_id < 0:
                    continue
                # Xác định hướng so với hàng đầu và hàng cuối
                horizontal = tiles[0][0] == tiles[-1][0]
                vehicles.append(
                    Vehicle(
                        id=vehicle_id,
                        tiles=tuple(tiles),
                        horizontal=horizontal
                    )
                )


            return Board(width=len(matrix), vehicles=tuple(vehicles))

    @staticmethod
    # load board.csv ->  
    def from_csv(file_path: str) -> "Board":
        return Board.from_matrix(csv_to_matrix(file_path=file_path))

    # Kiểm tra thắng thua
    def is_final_configuration(self) -> bool:
        return self.vehicles[0].tiles[-1][1] == self.width - 1

    # Hàm heuristic
    def get_minimum_cost(self) -> int:
        return (
            len(self.get_tiles_to_cover_by_red()) + self.minimum_steps_required_to_clear_direct_path()
        )

    # Số bước phải dịch xe khác để mở đường
    def minimum_steps_required_to_clear_direct_path(self) -> int:
        # Lấy các ô xe đỏ cần đi ra
        tiles_to_free = self.get_tiles_to_cover_by_red()
        total_steps = 0

        # Xét từng xe đang chắn
        for vehicle in self.vehicles_in_the_way_of_red():
            
            if len(vehicle.tiles) < 2:
                total_steps += 1
                continue
            
            for tile in tiles_to_free:
                # vị trí trùng xe đang chiếm
                if tile  in vehicle.tiles:

                    index = vehicle.tiles.index(tile)
                    '''
                    Nếu gần đầu xe -> đẩy ra đầu kia
                    Nếu gần cuối xe -> đẩy ra cuối kia
                    '''
                    steps = min(index+1,len(vehicle.tiles) - index)
                    total_steps += steps

        return total_steps

    # Các xe chắn đường
    def vehicles_in_the_way_of_red(self) -> Iterator[Vehicle]:
        tiles_to_free = self.get_tiles_to_cover_by_red()

        for vehicle in self.vehicles:
            # nếu chắn đường thoát xe chính -> xe chắn
            if any(tile in vehicle.tiles for tile in tiles_to_free):
                yield vehicle

    
    # Lấy danh sách mà các ô xe chính cần đi qua để đến đích
    def get_tiles_to_cover_by_red(self):
        
        red = self.vehicles[0] # xe chính
        row = red.tiles[-1][0]  # hàng xe chính
        start_col = red.tiles[-1][1] + 1    # cột sau đuôi xe
        
        return [(row,col) for col in range(start_col,self.width)]

    def get_moves(self) -> Iterator[Tuple[Move, int]]:
        for index, vehicle in enumerate(self.vehicles):
            forward_tile = None
            backward_tile = None

            # Xe nằm ngang
            if vehicle.horizontal:
                row = vehicle.tiles[0][0]

                # Xe ngang lùi
                leftmost_col = vehicle.tiles[0][1]
                if leftmost_col > 0:
                    backward_tile = (row, leftmost_col - 1)

                # Xe ngang tiến
                rightmost_col = vehicle.tiles[-1][1]
                if rightmost_col < self.width - 1:
                    forward_tile = (row, rightmost_col + 1)

            # Xe nằm dọc
            else:
                
                col = vehicle.tiles[0][1]

                # Xe dọc tiến
                bottom_row = vehicle.tiles[-1][0]
                if bottom_row < self.width - 1:
                    forward_tile = (bottom_row + 1, col)

                # Xe dọc lùi
                top_row = vehicle.tiles[0][0]
                if top_row > 0:
                    backward_tile = (top_row - 1, col)

            # Kiểm tra va chạm: nếu tile mới đã bị chiếm thì loại bỏ
            for other in self.vehicles:
                if forward_tile in other.tiles:
                    forward_tile = None
                if backward_tile in other.tiles:
                    backward_tile = None

            # Chi phí di chuyển (độ dài xe)
            cost = len(vehicle.tiles)

            # Yield các nước đi hợp lệ
            if forward_tile is not None:
                yield (Move(vehicle.id, index, move=1), cost)
            if backward_tile is not None:
                yield (Move(vehicle.id, index, move=-1), cost)



    def to_matrix(self) -> list[list[int]]:
        matrix = [[-1 for _ in range(self.width)] for _ in range(self.width)]
        for vehicle in self.vehicles:
            for tile in vehicle.tiles:
                matrix[tile[0]][tile[1]] = vehicle.id
        return matrix

    def __repr__(self):
        return str(self.to_matrix())

    def __hash__(self):
        return hash(self.vehicles)