import itertools
from collections import defaultdict

champion_data = {
    "니달리": {"traits": ["니트로", "증.폭."], "cost": 1, "name_kr": "니달리"},
    "모르가나": {"traits": ["신성기업", "다이나모"], "cost": 1, "name_kr": "모르가나"},
    "문도 박사": {"traits": ["거리의 악마", "난동꾼", "학살자"], "cost": 1, "name_kr": "문도 박사"},
    "바이": {"traits": ["사이퍼", "선봉대"], "cost": 1, "name_kr": "바이"}, 
    "뽀삐": {"traits": ["사이버보스", "요새"], "cost": 1, "name_kr": "뽀삐"}, 
    "사일러스": {"traits": ["동물특공대", "선봉대"], "cost": 1, "name_kr": "사일러스"},
    "샤코": {"traits": ["범죄 조직", "학살자"], "cost": 1, "name_kr": "샤코"},
    "세라핀": {"traits": ["동물특공대", "기술광"], "cost": 1, "name_kr": "세라핀"},
    "알리스타": {"traits": ["황금 황소", "난동꾼"], "cost": 1, "name_kr": "알리스타"},
    "자이라": {"traits": ["거리의 악마", "기술광"], "cost": 1, "name_kr": "자이라"},
    "잭스": {"traits": ["엑소테크", "요새"], "cost": 1, "name_kr": "잭스"},
    "코그모": {"traits": ["폭발봇", "속사포"], "cost": 1, "name_kr": "코그모"},
    "킨드레드": {"traits": ["니트로", "사격수", "속사포"], "cost": 1, "name_kr": "킨드레드"},
    "그레이브즈": {"traits": ["황금 황소", "처형자"], "cost": 2, "name_kr": "그레이브즈"},
    "나피리": {"traits": ["엑소테크", "증.폭."], "cost": 2, "name_kr": "나피리"},
    "다리우스": {"traits": ["범죄 조직", "난동꾼"], "cost": 2, "name_kr": "다리우스"},
    "라아스트": {"traits": ["신성기업", "선봉대"], "cost": 2, "name_kr": "라아스트"},
    "르블랑": {"traits": ["사이퍼", "기술광"], "cost": 2, "name_kr": "르블랑"},
    "베이가": {"traits": ["사이버보스", "기술광"], "cost": 2, "name_kr": "베이가"},
    "베인": {"traits": ["동물특공대", "학살자"], "cost": 2, "name_kr": "베인"},
    "쉬바나": {"traits": ["니트로", "기술광", "요새"], "cost": 2, "name_kr": "쉬바나"},
    "스카너": {"traits": ["폭발봇", "선봉대"], "cost": 2, "name_kr": "스카너"},
    "에코": {"traits": ["거리의 악마", "책략가"], "cost": 2, "name_kr": "에코"},
    "일라오이": {"traits": ["동물특공대", "요새"], "cost": 2, "name_kr": "일라오이"},
    "진": {"traits": ["엑소테크", "다이나모"], "cost": 2, "name_kr": "진"},
    "트위스티드 페이트": {"traits": ["범죄 조직", "속사포"], "cost": 2, "name_kr": "트위스티드 페이트"},
    "갈리오": {"traits": ["사이퍼", "요새"], "cost": 3, "name_kr": "갈리오"},
    "그라가스": {"traits": ["신성기업", "난동꾼"], "cost": 3, "name_kr": "그라가스"},
    "드레이븐": {"traits": ["사이퍼", "속사포"], "cost": 3, "name_kr": "드레이븐"},
    "렝가": {"traits": ["거리의 악마", "처형자"], "cost": 3, "name_kr": "렝가"},
    "모데카이저": {"traits": ["엑소테크", "기술광", "난동꾼"], "cost": 3, "name_kr": "모데카이저"},
    "바루스": {"traits": ["엑소테크", "처형자"], "cost": 3, "name_kr": "바루스"},
    "브라움": {"traits": ["범죄 조직", "선봉대"], "cost": 3, "name_kr": "브라움"},
    "세나": {"traits": ["신성기업", "학살자"], "cost": 3, "name_kr": "세나"},
    "엘리스": {"traits": ["니트로", "다이나모"], "cost": 3, "name_kr": "엘리스"},
    "유미": {"traits": ["동물특공대", "증.폭.", "책략가"], "cost": 3, "name_kr": "유미"},
    "자르반 4세": {"traits": ["황금 황소", "선봉대", "학살자"], "cost": 3, "name_kr": "자르반 4세"},
    "징크스": {"traits": ["거리의 악마", "사격수"], "cost": 3, "name_kr": "징크스"},
    "피들스틱": {"traits": ["폭발봇", "기술광"], "cost": 3, "name_kr": "피들스틱"},
    "니코": {"traits": ["거리의 악마", "책략가"], "cost": 4, "name_kr": "니코"},
    "레오나": {"traits": ["동물특공대", "선봉대"], "cost": 4, "name_kr": "레오나"},
    "미스 포츈": {"traits": ["범죄 조직", "다이나모"], "cost": 4, "name_kr": "미스 포츈"},
    "벡스": {"traits": ["신성기업", "처형자"], "cost": 4, "name_kr": "벡스"},
    "브랜드": {"traits": ["거리의 악마", "기술광"], "cost": 4, "name_kr": "브랜드"},
    "세주아니": {"traits": ["엑소테크", "요새"], "cost": 4, "name_kr": "세주아니"},
    "아펠리오스": {"traits": ["황금 황소", "사격수"], "cost": 4, "name_kr": "아펠리오스"},
    "애니": {"traits": ["황금 황소", "증.폭."], "cost": 4, "name_kr": "애니"},
    "자야": {"traits": ["동물특공대", "사격수"], "cost": 4, "name_kr": "자야"},
    "제드": {"traits": ["사이퍼", "학살자"], "cost": 4, "name_kr": "제드"},
    "제리": {"traits": ["엑소테크", "속사포"], "cost": 4, "name_kr": "제리"},
    "직스": {"traits": ["사이버보스", "책략가"], "cost": 4, "name_kr": "직스"},
    "초가스": {"traits": ["폭발봇", "난동꾼"], "cost": 4, "name_kr": "초가스"},
    "가렌": {"traits": ["네트워크의 신"], "cost": 5, "name_kr": "가렌"},
    "레넥톤": {"traits": ["신성기업", "군주", "요새"], "cost": 5, "name_kr": "레넥톤"},
    "비에고": {"traits": ["황금 황소", "영혼 살해자", "기술광"], "cost": 5, "name_kr": "비에고"},
    "사미라": {"traits": ["거리의 악마", "증.폭."], "cost": 5, "name_kr": "사미라"},
    "오로라": {"traits": ["동물특공대", "다이나모"], "cost": 5, "name_kr": "오로라"},
    "우르곳": {"traits": ["폭발봇", "처형자"], "cost": 5, "name_kr": "우르곳"},
    "자크": {"traits": ["바이러스"], "cost": 5, "name_kr": "자크"},
    "코부코": {"traits": ["사이버보스", "난동꾼"], "cost": 5, "name_kr": "코부코"},
}
trait_data = {
    "기술광": {"breakpoints": [2, 4, 6, 8], "name_kr": "기술광"},
    "난동꾼": {"breakpoints": [2, 4, 6], "name_kr": "난동꾼"},
    "다이나모": {"breakpoints": [2, 3, 4], "name_kr": "다이나모"},
    "사격수": {"breakpoints": [2, 4], "name_kr": "사격수"},
    "선봉대": {"breakpoints": [2, 4, 6], "name_kr": "선봉대"},
    "속사포": {"breakpoints": [2, 4, 6], "name_kr": "속사포"},
    "요새": {"breakpoints": [2, 4, 6], "name_kr": "요새"},
    "증.폭.": {"breakpoints": [2, 3, 4, 5], "name_kr": "증.폭."},
    "책략가": {"breakpoints": [2, 3, 4, 5], "name_kr": "책략가"},
    "처형자": {"breakpoints": [2, 3, 4, 5], "name_kr": "처형자"},
    "학살자": {"breakpoints": [2, 4, 6], "name_kr": "학살자"},
    "거리의 악마": {"breakpoints": [3, 5, 7, 10], "name_kr": "거리의 악마"},
    "군주": {"breakpoints": [1], "name_kr": "군주"},
    "네트워크의 신": {"breakpoints": [1], "name_kr": "네트워크의 신"},
    "니트로": {"breakpoints": [3, 4], "name_kr": "니트로"},
    "엑소테크": {"breakpoints": [3, 5, 7, 10], "name_kr": "엑소테크"},
    "사이버보스": {"breakpoints": [2, 3, 4], "name_kr": "사이버보스"},
    "신성기업": {"breakpoints": [1, 2, 3, 4, 5, 6, 7], "name_kr": "신성기업"},
    "범죄 조직": {"breakpoints": [3, 5, 7], "name_kr": "범죄 조직"},
    "동물특공대": {"breakpoints": [3, 5, 7, 10], "name_kr": "동물특공대"},
    "폭발봇": {"breakpoints": [2, 4, 6], "name_kr": "폭발봇"},
    "사이퍼": {"breakpoints": [3, 4, 5], "name_kr": "사이퍼"},
    "황금 황소": {"breakpoints": [2, 4, 6], "name_kr": "황금 황소"},
    "바이러스": {"breakpoints": [1], "name_kr": "바이러스"},
    "영혼 살해자": {"breakpoints": [1], "name_kr": "영혼 살해자"}, 
}

MAX_CHAMPS_FOR_HOLDER_CANDIDATES = 15 
MAX_LOCAL_SEARCH_ITERATIONS = 5 

EXCLUDED_TRAITS_FOR_DIVERSITY_SCORING = {
    "바이러스", 
    "영혼 살해자",
    "군주", 
    "네트워크의 신"  
}

def calculate_active_synergies_multi(team_champion_names, emblem_assignments_map, current_champion_data, current_trait_data):
    trait_counts = defaultdict(int)
    for champ_name in team_champion_names:
        champ_original_traits = list(current_champion_data.get(champ_name, {}).get("traits", []))
        assigned_emblem_trait = emblem_assignments_map.get(champ_name)
        current_champ_all_traits = list(champ_original_traits)
        if assigned_emblem_trait and assigned_emblem_trait not in current_champ_all_traits:
            current_champ_all_traits.append(assigned_emblem_trait)
        for trait in set(current_champ_all_traits):
            trait_counts[trait] += 1
            
    active_synergies = {}
    for trait_name, count in trait_counts.items():
        if trait_name in current_trait_data: 
            if current_trait_data[trait_name].get("breakpoints"):
                for bp in sorted(current_trait_data[trait_name]["breakpoints"], reverse=True):
                    if count >= bp:
                        active_synergies[trait_name] = bp
                        break
    return active_synergies

def evaluate_composition_score_diversity(active_synergies_map, current_trait_data):
    diversity_score = 0
    for trait_name, level in active_synergies_map.items():
        if level > 0: 
            if trait_name not in EXCLUDED_TRAITS_FOR_DIVERSITY_SCORING:
                diversity_score += 1 
    return diversity_score


def find_optimal_tft_composition_final_version(
    all_champion_data, 
    all_trait_data, 
    parsed_emblem_specs, 
    board_size
):
    best_composition_names = []
    best_synergies = {}
    max_score = -1 
    best_emblem_assignments = {}

    all_champion_names_list = list(all_champion_data.keys())

    def sort_heuristic(champ_name):
        data = all_champion_data.get(champ_name, {"cost": 0, "traits": []})
        return (data["cost"], len(data["traits"]), champ_name)

    if not parsed_emblem_specs:
        print("상징 정보 없음: 다양성 최대화 조합 탐색 (Greedy + Local Search)...")
        current_best_team_no_emblem = []
        for _ in range(board_size): # Greedy 초기 해 구성
            best_next_filler = None
            highest_diversity_for_slot = -1
            candidate_fillers = [c for c in all_champion_names_list if c not in current_best_team_no_emblem]
            if not candidate_fillers: break

            for candidate_champ in candidate_fillers:
                prospective_team = current_best_team_no_emblem + [candidate_champ]
                active_syns = calculate_active_synergies_multi(prospective_team, {}, all_champion_data, all_trait_data)
                current_diversity = evaluate_composition_score_diversity(active_syns, all_trait_data)
                
                if current_diversity > highest_diversity_for_slot:
                    highest_diversity_for_slot = current_diversity
                    best_next_filler = candidate_champ
                elif current_diversity == highest_diversity_for_slot and best_next_filler:
                    if sort_heuristic(candidate_champ) > sort_heuristic(best_next_filler):
                        best_next_filler = candidate_champ
            
            if best_next_filler:
                current_best_team_no_emblem.append(best_next_filler)
            else:
                if len(current_best_team_no_emblem) < board_size and candidate_fillers:
                     candidate_fillers.sort(key=sort_heuristic, reverse=True)
                     current_best_team_no_emblem.append(candidate_fillers[0]) 
                else: break
        
        if len(current_best_team_no_emblem) == board_size:
            current_best_synergies = calculate_active_synergies_multi(current_best_team_no_emblem, {}, all_champion_data, all_trait_data)
            current_max_diversity = evaluate_composition_score_diversity(current_best_synergies, all_trait_data)

            # Local Search
            for _ in range(MAX_LOCAL_SEARCH_ITERATIONS):
                improved_in_this_ls_iteration = False
                team_to_improve = list(current_best_team_no_emblem) # 현재 최선 팀 복사
                
                for i in range(len(team_to_improve)):
                    original_champ_to_swap = team_to_improve[i]
                    base_team_for_swap = team_to_improve[:i] + team_to_improve[i+1:]
                    swap_candidates = [c for c in all_champion_names_list if c not in base_team_for_swap] 
                    
                    for new_champ_candidate in swap_candidates:
                        if new_champ_candidate == original_champ_to_swap: continue # 같은 챔피언으로 교체 시도 방지

                        potential_swapped_team = base_team_for_swap + [new_champ_candidate]
                        if len(set(potential_swapped_team)) != board_size: continue 

                        swapped_active_syns = calculate_active_synergies_multi(potential_swapped_team, {}, all_champion_data, all_trait_data)
                        swapped_diversity_score = evaluate_composition_score_diversity(swapped_active_syns, all_trait_data)
                        
                        current_team_cost = sum(all_champion_data.get(c, {}).get('cost',0) for c in team_to_improve)
                        potential_swapped_team_cost = sum(all_champion_data.get(c, {}).get('cost',0) for c in potential_swapped_team)

                        if swapped_diversity_score > current_max_diversity or \
                           (swapped_diversity_score == current_max_diversity and potential_swapped_team_cost > current_team_cost):
                            team_to_improve = sorted(potential_swapped_team) # 개선된 팀으로 업데이트
                            current_max_diversity = swapped_diversity_score
                            current_best_synergies = swapped_active_syns
                            improved_in_this_ls_iteration = True
                
                if improved_in_this_ls_iteration:
                    current_best_team_no_emblem = team_to_improve # 반복 개선된 팀을 현재 최선으로 확정
                else:
                    break 
            
            # 최종적으로 찾은 최적해를 함수 전체의 best 값들과 비교/업데이트
            if current_max_diversity > max_score:
                max_score = current_max_diversity
                best_composition_names = sorted(current_best_team_no_emblem)
                best_synergies = current_best_synergies
                best_emblem_assignments = {}
            elif current_max_diversity == max_score and (not best_composition_names or \
                 sum(all_champion_data.get(c, {}).get('cost',0) for c in current_best_team_no_emblem) > \
                 sum(all_champion_data.get(c, {}).get('cost',0) for c in best_composition_names)):
                    best_composition_names = sorted(current_best_team_no_emblem)
                    best_synergies = current_best_synergies
                    best_emblem_assignments = {}
        
        return best_composition_names, best_synergies, max_score, best_emblem_assignments

    individual_emblems_to_assign = []
    for spec in parsed_emblem_specs:
        individual_emblems_to_assign.extend([spec['trait']] * spec['count'])
    
    num_total_holders_needed = len(individual_emblems_to_assign)

    if num_total_holders_needed > board_size:
        print(f"오류: 총 상징 보유자 수({num_total_holders_needed}) > 배치 기물 수({board_size})")
        return [], {}, -1, {}

    num_filler_units_needed = board_size - num_total_holders_needed
    if num_filler_units_needed < 0: return [], {}, -1, {}

    holder_candidate_pool_full = sorted(all_champion_names_list, key=sort_heuristic, reverse=True)
    holder_candidate_pool = holder_candidate_pool_full[:MAX_CHAMPS_FOR_HOLDER_CANDIDATES]

    if len(holder_candidate_pool) < num_total_holders_needed:
        holder_candidate_pool = holder_candidate_pool_full 
        if len(holder_candidate_pool) < num_total_holders_needed:
            print("오류: 상징 부여할 챔피언 후보 부족.")
            return [], {}, -1, {}

    for holder_names_tuple in itertools.combinations(holder_candidate_pool, num_total_holders_needed):
        current_holder_names = list(holder_names_tuple)
        unique_emblem_assignment_sequences = list(set(itertools.permutations(individual_emblems_to_assign)))

        for permuted_emblem_traits in unique_emblem_assignment_sequences:
            current_emblem_assignments = {}
            for i, holder_name in enumerate(current_holder_names):
                current_emblem_assignments[holder_name] = permuted_emblem_traits[i]

            team_after_emblems = list(current_holder_names) 
            greedy_filled_team = list(team_after_emblems) 
            
            for _ in range(num_filler_units_needed):
                best_next_filler = None
                highest_diversity_for_this_slot = -1 
                candidate_fillers_for_slot = [c for c in all_champion_names_list if c not in greedy_filled_team]
                if not candidate_fillers_for_slot: break

                for candidate_champ in candidate_fillers_for_slot:
                    prospective_team = greedy_filled_team + [candidate_champ]
                    active_syns_greedy = calculate_active_synergies_multi(
                        prospective_team, current_emblem_assignments, all_champion_data, all_trait_data
                    )
                    current_diversity_score = evaluate_composition_score_diversity(active_syns_greedy, all_trait_data)

                    if current_diversity_score > highest_diversity_for_this_slot:
                        highest_diversity_for_this_slot = current_diversity_score
                        best_next_filler = candidate_champ
                    elif current_diversity_score == highest_diversity_for_this_slot and best_next_filler:
                         if sort_heuristic(candidate_champ) > sort_heuristic(best_next_filler):
                            best_next_filler = candidate_champ
                
                if best_next_filler:
                    greedy_filled_team.append(best_next_filler)
                else:
                    if len(greedy_filled_team) < board_size and candidate_fillers_for_slot:
                        candidate_fillers_for_slot.sort(key=sort_heuristic, reverse=True)
                        greedy_filled_team.append(candidate_fillers_for_slot[0]) 
                    else:
                        break
            
            if len(greedy_filled_team) == board_size:
                final_team_candidate_names = greedy_filled_team
                active_syns = calculate_active_synergies_multi(
                    final_team_candidate_names, current_emblem_assignments, all_champion_data, all_trait_data
                )
                current_score = evaluate_composition_score_diversity(active_syns, all_trait_data)

                if current_score > max_score:
                    max_score = current_score
                    best_composition_names = sorted(final_team_candidate_names)
                    best_synergies = active_syns
                    best_emblem_assignments = current_emblem_assignments.copy()
                elif current_score == max_score and best_composition_names:
                    current_comp_cost = sum(all_champion_data.get(c, {}).get('cost',0) for c in final_team_candidate_names)
                    best_comp_cost = sum(all_champion_data.get(c, {}).get('cost',0) for c in best_composition_names)
                    if current_comp_cost > best_comp_cost:
                        best_composition_names = sorted(final_team_candidate_names)
                        best_synergies = active_syns
                        best_emblem_assignments = current_emblem_assignments.copy()
    
    return best_composition_names, best_synergies, max_score, best_emblem_assignments

if __name__ == "__main__":
    print("롤토체스 유연함 탐색기 (다중 상징 입력 지원, 특정 특성 제외한 다양성 최대화)")
    
    emblem_traits_str = input("상징 특성 입력 (예: 범죄 조직,속사포 또는 엔터 시 상징 없음): ")
    
    parsed_emblem_specs = [] 
    proceed_to_board_size = False 

    if emblem_traits_str.strip(): 
        emblem_counts_str = input("각 상징 개수 입력 (예: 2,1 또는 1): ")
        try:
            trait_names = [trait.strip() for trait in emblem_traits_str.split(',')]
            trait_counts = [int(count.strip()) for count in emblem_counts_str.split(',')]

            if len(trait_names) != len(trait_counts):
                print("오류: 입력된 특성 이름의 수와 개수의 수가 일치하지 않습니다.")
            else:
                valid_input = True
                for i in range(len(trait_names)):
                    if not trait_names[i]:
                        print(f"오류: {i+1}번째 특성 이름이 비어있습니다.")
                        valid_input = False; break
                    if trait_counts[i] < 0:
                        print(f"오류: {trait_names[i]} 특성의 개수가 0보다 작을 수 없습니다.")
                        valid_input = False; break
                    if trait_names[i] not in trait_data: 
                        print(f"경고: 특성 목록에 없는 특성 이름입니다 - '{trait_names[i]}'. 해당 상징은 무시됩니다.")
                        continue 
                    if trait_counts[i] > 0 :
                        parsed_emblem_specs.append({'trait': trait_names[i], 'count': trait_counts[i]})
                
                if not valid_input: 
                    parsed_emblem_specs = "ERROR" 
                elif not parsed_emblem_specs and emblem_traits_str.strip(): 
                    print("경고: 모든 상징 개수가 0이거나 유효하지 않은 특성명으로 입력되어, 상징 없이 탐색합니다.")
                    proceed_to_board_size = True 
                elif parsed_emblem_specs : 
                     proceed_to_board_size = True
        except ValueError:
            print("오류: 상징 개수에 잘못된 숫자 형식이 입력되었습니다.")
            parsed_emblem_specs = "ERROR"
    else: 
        print("정보: 상징 없이 탐색합니다.")
        proceed_to_board_size = True
    
    if parsed_emblem_specs != "ERROR" and proceed_to_board_size:
        try:
            target_board_size_str = input("배치 기물 수 입력 (예: 8): ")
            if not target_board_size_str.strip(): 
                 print("오류: 배치 기물 수가 입력되지 않았습니다. 기본값 8로 설정합니다.")
                 target_board_size = 8
            else:
                 target_board_size = int(target_board_size_str)
            
            if target_board_size <= 0:
                print("오류: 배치 기물 수는 0보다 커야 합니다.")
            else:
                if parsed_emblem_specs:
                    print(f"\n입력 조건: {len(parsed_emblem_specs)} 종류의 상징 ({sum(s['count'] for s in parsed_emblem_specs)}개), 배치 기물 수 {target_board_size}\n")
                    for spec in parsed_emblem_specs:
                        print(f"  - {trait_data.get(spec['trait'], {}).get('name_kr', spec['trait'])}: {spec['count']}개")
                else:
                    print(f"\n입력 조건: 상징 없음, 배치 기물 수 {target_board_size}\n")

                print(f"최적 조합 탐색 중 (제외 특성 반영, 다양성 최대화)...")
                
                best_comp, best_syn, score, best_assignments = find_optimal_tft_composition_final_version(
                    champion_data, trait_data, parsed_emblem_specs, target_board_size
                )

                if best_comp:
                    print("\n--- 최적 조합 결과 ---")
                    print(f"챔피언 조합 ({len(best_comp)}명):")
                    for name in best_comp:
                        champ_info = champion_data.get(name, {})
                        name_kr = champ_info.get('name_kr', name)
                        print(f"- {name_kr} ({name})")
                    
                    print("\n활성 시너지:")
                    sorted_synergies = sorted(best_syn.items(), key=lambda item: trait_data.get(item[0], {}).get('name_kr', item[0]))
                    for trait, level in sorted_synergies:
                        trait_info = trait_data.get(trait, {})
                        trait_name_kr = trait_info.get('name_kr', trait)
                        is_excluded_from_score = " (점수 계산 제외)" if trait in EXCLUDED_TRAITS_FOR_DIVERSITY_SCORING else ""
                        print(f"- {trait_name_kr} {level}{is_excluded_from_score} ({trait} {level})")
                    
                    print(f"\n계산된 다양성 점수 (제외 특성 반영): {score}") 

                    if best_assignments:
                        print("\n상세 상징 할당:")
                        sorted_assignments = sorted(best_assignments.items(), key=lambda item: champion_data.get(item[0], {}).get('name_kr', item[0]))
                        for champ_name_en, trait_name_en in sorted_assignments:
                            champ_info = champion_data.get(champ_name_en, {})
                            trait_info = trait_data.get(trait_name_en, {})
                            champ_name_kr = champ_info.get('name_kr', champ_name_en)
                            trait_name_kr = trait_info.get('name_kr', trait_name_en)
                            print(f"- {champ_name_kr} ({champ_name_en}): {trait_name_kr} ({trait_name_en}) 상징")
                    elif parsed_emblem_specs :
                         print("\n참고: 상징이 입력되었으나, 최종 조합에서 해당 상징이 최적해에 포함되지 않았거나 할당 정보가 없을 수 있습니다.")
                else:
                    print("조건에 맞는 조합을 찾지 못했습니다.")
        except ValueError:
             print("오류: 배치 기물 수에 잘못된 숫자 형식이 입력되었습니다.")
        except Exception as e:
            print(f"탐색 또는 실행 중 알 수 없는 오류 발생: {e}")

    elif parsed_emblem_specs == "ERROR": 
        print("입력 오류로 인해 탐색을 진행하지 않습니다.")