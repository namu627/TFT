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
    "기술광": {"breakpoints": [2,4,6,8], "name_kr": "기술광"},
    "난동꾼": {"breakpoints": [2,4,6], "name_kr": "난동꾼"},
    "다이나모": {"breakpoints": [2,3,4], "name_kr": "다이나모"},
    "사격수": {"breakpoints": [2,4], "name_kr": "사격수"},
    "선봉대": {"breakpoints": [2,4,6], "name_kr": "선봉대"}, 
    "속사포": {"breakpoints": [2,4,6], "name_kr": "속사포"}, 
    "요새": {"breakpoints": [2,4,6], "name_kr": "요새"}, 
    "증.폭.": {"breakpoints": [2,3,4,5], "name_kr": "증.폭."},
    "책략가": {"breakpoints": [2,3,4,5], "name_kr": "책략가"}, 
    "처형자": {"breakpoints": [2,3,4,5], "name_kr": "처형자"}, 
    "학살자": {"breakpoints": [2,4,6], "name_kr": "학살자"},
    "거리의 악마": {"breakpoints": [3,5,7,10], "name_kr": "거리의 악마"},
    "군주": {"breakpoints": [1], "name_kr": "군주"},
    "네트워크의 신": {"breakpoints": [1], "name_kr": "네트워크의 신"},
    "니트로": {"breakpoints": [3,4], "name_kr": "니트로"},
    "엑소테크": {"breakpoints": [3,5,7,10], "name_kr": "엑소테크"},
    "사이버보스": {"breakpoints": [2,3,4], "name_kr": "사이버보스"},
    "신성기업": {"breakpoints": [1,2,3,4,5,6,7], "name_kr": "신성기업"},
    "범죄 조직": {"breakpoints": [3,5,7], "name_kr": "범죄 조직"},
    "동물특공대": {"breakpoints": [3,5,7,10], "name_kr": "동물특공대"},
    "폭발봇": {"breakpoints": [2,4,6], "name_kr": "폭발봇"},
    "사이퍼": {"breakpoints": [3,4,5], "name_kr": "사이퍼"},
    "황금 황소": {"breakpoints": [2,4,6], "name_kr": "황금 황소"},
    "바이러스": {"breakpoints": [1], "name_kr": "바이러스"},
    "영혼 살해자": {"breakpoints": [1], "name_kr": "영혼 살해자"},
}

MAX_CHAMPS_FOR_CORE_POOL = 10      
MAX_CHAMPS_FOR_EMBLEM_HOLDER_POOL = 12 
MAX_CHAMPS_FOR_SECONDARY_HOLDER_POOL = 12 # 부가 상징 보유자 후보군 제한


PRIORITY_TRAIT_WEIGHT = 100

def calculate_active_synergies_multi(team_champion_names, emblem_assignments_map, current_champion_data, current_trait_data):
    """
    주어진 팀 조합과 상징 할당 정보를 바탕으로 활성화된 시너지와 그 레벨을 계산합니다.
    emblem_assignments_map: {'챔피언명': '부여된특성명'}
    """
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
            for bp in sorted(current_trait_data[trait_name]["breakpoints"], reverse=True):
                if count >= bp:
                    active_synergies[trait_name] = bp
                    break
    return active_synergies

def evaluate_composition_score_multi(active_synergies_map, current_trait_data, emblem_traits_for_priority_list):
    priority_traits_score = 0
    other_traits_score = 0

    for trait, level in active_synergies_map.items():
        if trait in emblem_traits_for_priority_list: # 우선순위 특성 목록에 있는지 확인
            priority_traits_score += level * PRIORITY_TRAIT_WEIGHT
        else:
            other_traits_score += level 
            trait_info = current_trait_data.get(trait)
            if trait_info and trait_info.get("breakpoints"):
                if trait_info["breakpoints"]:
                     max_bp_for_trait = sorted(trait_info["breakpoints"])[-1]
                     min_level_for_bonus = 2 if max_bp_for_trait <= 3 else 3
                     if level >= max_bp_for_trait * 0.6 and level >= min_level_for_bonus :
                          other_traits_score += level * 0.2 
                elif level > 0 : 
                    other_traits_score += level * 0.1
                
    return priority_traits_score + other_traits_score

def find_optimal_tft_composition_multi_emblem(
    all_champion_data, 
    all_trait_data, 
    parsed_emblem_specs,
    board_size
):
    best_composition_names = []
    best_synergies = {}
    max_score = -1

    if not parsed_emblem_specs:
        print("오류: 상징 정보가 제공되지 않았습니다.")
        return [], {}, -1

    all_champion_names_list = list(all_champion_data.keys())

    def sort_heuristic(champ_name):
        data = all_champion_data.get(champ_name, {"cost": 0, "traits": []})
        return (data["cost"], len(data["traits"]))

    primary_emblem_spec = parsed_emblem_specs[0]
    primary_emblem_trait = primary_emblem_spec['trait']
    primary_emblem_count = primary_emblem_spec['count']

    secondary_emblem_specs = parsed_emblem_specs[1:]

    all_input_emblem_traits = [spec['trait'] for spec in parsed_emblem_specs]

    raw_native_to_primary_champs = [
        name for name, data in all_champion_data.items() 
        if primary_emblem_trait in data.get("traits", [])
    ]
    raw_native_to_primary_champs.sort(key=sort_heuristic, reverse=True)
    native_to_primary_champs_pool = raw_native_to_primary_champs[:MAX_CHAMPS_FOR_CORE_POOL]

    sorted_all_champs_for_holders = sorted(all_champion_names_list, key=sort_heuristic, reverse=True)


    if primary_emblem_trait not in all_trait_data:
        print(f"오류: 주요 상징 특성 '{primary_emblem_trait}'에 대한 데이터가 없습니다.")
        return [], {}, -1
        
    for target_bp in sorted(all_trait_data[primary_emblem_trait]["breakpoints"], reverse=True):
        if target_bp == 0: continue

        natural_units_for_primary = target_bp - primary_emblem_count
        if natural_units_for_primary < 0: natural_units_for_primary = 0
        
        current_core_candidates = native_to_primary_champs_pool
        if len(native_to_primary_champs_pool) < natural_units_for_primary:
            if len(raw_native_to_primary_champs) >= natural_units_for_primary:
                 current_core_candidates = raw_native_to_primary_champs 
            else: 
                 continue
        
        for core_natural_champs_tuple in itertools.combinations(current_core_candidates, natural_units_for_primary):
            core_natural_champs = list(core_natural_champs_tuple)
            current_emblem_assignments = {} # 최종 상징 할당 맵

            potential_primary_holders = [
                c for c in sorted_all_champs_for_holders 
                if c not in core_natural_champs and primary_emblem_trait not in all_champion_data[c].get("traits",[])
            ][:MAX_CHAMPS_FOR_EMBLEM_HOLDER_POOL] # 주요 특성이 없는 챔피언 중에서 후보 선정 및 제한

            if len(potential_primary_holders) < primary_emblem_count: continue

            for primary_holder_names_tuple in itertools.combinations(potential_primary_holders, primary_emblem_count):
                primary_holder_names = list(primary_holder_names_tuple)
                
                temp_assignments_after_primary = {}
                for holder_name in primary_holder_names:
                    temp_assignments_after_primary[holder_name] = primary_emblem_trait
                
                team_after_primary = core_natural_champs + primary_holder_names

                individual_secondary_emblems = []
                for spec in secondary_emblem_specs:
                    individual_secondary_emblems.extend([spec['trait']] * spec['count'])
                
                num_secondary_holders_needed = len(individual_secondary_emblems)

                potential_secondary_holders_pool = [
                    c for c in sorted_all_champs_for_holders 
                    if c not in team_after_primary # 주요팀에 없는 챔피언 중
                ][:MAX_CHAMPS_FOR_SECONDARY_HOLDER_POOL] # 후보군 제한

                if len(potential_secondary_holders_pool) < num_secondary_holders_needed: 
                    if num_secondary_holders_needed == 0: # 부가 상징이 없으면 바로 필러 단계로
                        pass
                    else: # 부가 상징 필요한데 후보 부족
                        continue
                
                # 부가 상징이 없는 경우, 이 루프는 한 번만 (빈 리스트로) 실행됨
                secondary_holder_comb_iter = itertools.combinations(potential_secondary_holders_pool, num_secondary_holders_needed) if num_secondary_holders_needed > 0 else [()]

                for secondary_holder_names_tuple in secondary_holder_comb_iter:
                    secondary_holder_names = list(secondary_holder_names_tuple)
                    
                    # 선택된 부가 상징 보유자들에게 부가 상징들을 할당하는 모든 경우의 수 (순열)
                    unique_secondary_emblem_permutations = list(set(itertools.permutations(individual_secondary_emblems))) if num_secondary_holders_needed > 0 else [()]

                    for s_emblem_perm in unique_secondary_emblem_permutations:
                        current_emblem_assignments.clear()
                        current_emblem_assignments.update(temp_assignments_after_primary) # 주요 상징 할당 복사

                        valid_secondary_assignment = True
                        temp_secondary_assignments = {}
                        for i, s_holder_name in enumerate(secondary_holder_names):
                            # 이미 주요 상징을 받은 챔피언이 부가 상징을 또 받을 수 없음 (여기선 holder가 다르므로 괜찮음)
                            # 한 챔피언이 여러 다른 종류의 상징을 동시에 받는 것은 불가 (TFT 규칙 상)
                            temp_secondary_assignments[s_holder_name] = s_emblem_perm[i]
                        
                        # 혹시 모를 중복 할당 방지 (이론상으론 발생 안해야 함)
                        for ch, tr in temp_secondary_assignments.items():
                            if ch in current_emblem_assignments and current_emblem_assignments[ch] != tr:
                                valid_secondary_assignment = False; break
                            current_emblem_assignments[ch] = tr
                        if not valid_secondary_assignment: continue
                            
                        team_after_all_emblems = core_natural_champs + primary_holder_names + secondary_holder_names
                        
                        greedy_filled_team = list(team_after_all_emblems)
                        num_fillers_to_add = board_size - len(greedy_filled_team)

                        if num_fillers_to_add < 0: continue 

                        for _ in range(num_fillers_to_add):
                            best_next_filler = None
                            highest_score_for_this_slot = -1 

                            candidate_fillers_for_slot = [
                                c for c in all_champion_names_list 
                                if c not in greedy_filled_team 
                            ]
                            if not candidate_fillers_for_slot: break

                            for candidate_champ in candidate_fillers_for_slot:
                                prospective_team = greedy_filled_team + [candidate_champ]
                                active_syns_greedy = calculate_active_synergies_multi(
                                    prospective_team, current_emblem_assignments, 
                                    all_champion_data, all_trait_data
                                )
                                current_greedy_score = evaluate_composition_score_multi(
                                    active_syns_greedy, all_trait_data, all_input_emblem_traits 
                                )

                                if current_greedy_score > highest_score_for_this_slot:
                                    highest_score_for_this_slot = current_greedy_score
                                    best_next_filler = candidate_champ
                            
                            if best_next_filler:
                                greedy_filled_team.append(best_next_filler)
                            else:
                                break 
                        
                        if len(greedy_filled_team) == board_size:
                            final_team_candidate_names = greedy_filled_team
                            active_syns = calculate_active_synergies_multi(
                                final_team_candidate_names, current_emblem_assignments,    
                                all_champion_data, all_trait_data
                            )
                            current_score = evaluate_composition_score_multi(
                                active_syns, all_trait_data, all_input_emblem_traits
                            )

                            if current_score > max_score:
                                max_score = current_score
                                best_composition_names = sorted(final_team_candidate_names)
                                best_synergies = active_syns
    
    return best_composition_names, best_synergies, max_score

if __name__ == "__main__":
    print("롤토체스 최적 조합 탐색기 (다중 상징 입력 지원)")
    
    emblem_traits_str = input("상징 특성 입력 (예: 범죄 조직,속사포 또는 난동꾼): ")
    emblem_counts_str = input("각 상징 개수 입력 (예: 2,1 또는 1): ")
    target_board_size = int(input("배치 기물 수 입력 (예: 8): "))

    try:
        trait_names = [trait.strip() for trait in emblem_traits_str.split(',')]
        trait_counts = [int(count.strip()) for count in emblem_counts_str.split(',')]

        if len(trait_names) != len(trait_counts):
            print("오류: 입력된 특성 이름의 수와 개수의 수가 일치하지 않습니다.")
        else:
            parsed_emblem_specs = []
            for i in range(len(trait_names)):
                if not trait_names[i]: # 빈 특성 이름 방지
                    print(f"오류: {i+1}번째 특성 이름이 비어있습니다.")
                    parsed_emblem_specs = [] # 오류 시 초기화
                    break
                if trait_counts[i] < 0:
                     print(f"오류: {trait_names[i]} 특성의 개수가 0보다 작을 수 없습니다.")
                     parsed_emblem_specs = []
                     break
                if trait_counts[i] > 0 : # 개수가 0인 상징은 추가하지 않음
                    parsed_emblem_specs.append({'trait': trait_names[i], 'count': trait_counts[i]})
            
            if not parsed_emblem_specs and emblem_traits_str.strip(): 
                 if not any(tc > 0 for tc in trait_counts) : print("경고: 모든 상징 개수가 0이거나 유효하지 않아, 상징 없이 탐색합니다.")
            
            if parsed_emblem_specs: 
                primary_trait_for_display = trait_data.get(parsed_emblem_specs[0]['trait'], {}).get('name_kr', parsed_emblem_specs[0]['trait'])
                print(f"\n입력 조건: 주요 상징 특성 '{primary_trait_for_display}', 총 {sum(s['count'] for s in parsed_emblem_specs)}개 상징, 배치 기물 수 {target_board_size}\n")
                all_input_emblem_traits_for_log = [spec['trait'] for spec in parsed_emblem_specs]
                print(f"최적 조합 탐색 중 (우선 특성: {all_input_emblem_traits_for_log}, ...")
                
                best_comp, best_syn, score = find_optimal_tft_composition_multi_emblem(
                    champion_data, 
                    trait_data,    
                    parsed_emblem_specs,
                    target_board_size
                )

                if best_comp:
                    print("\n--- 최적 조합 결과 ---")
                    print(f"챔피언 조합 ({len(best_comp)}명):")
                    for name in best_comp:
                        champ_info = champion_data.get(name, {})
                        name_kr = champ_info.get('name_kr', name)
                        print(f"- {name_kr}")
                    
                    print("\n활성 시너지 (입력된 모든 상징 특성 우선):")

                    sorted_synergies = sorted(best_syn.items(), key=lambda item: item[0] not in all_input_emblem_traits_for_log)

                    for trait, level in sorted_synergies:
                        trait_info = trait_data.get(trait, {})
                        trait_name_kr = trait_info.get('name_kr', trait)
                        is_priority = " (입력 상징)" if trait in all_input_emblem_traits_for_log else ""
                        print(f"- {trait_name_kr} {level}{is_priority}")
                else:
                    print("조건에 맞는 조합을 찾지 못했습니다.")
            elif not emblem_traits_str.strip(): # 아예 상징 입력이 없는 경우 (예: 엔터만 친 경우)
                 print("상징이 입력되지 않았습니다. 상징 없이 탐색하는 기능은 현재 미구현입니다.") # 또는 기본 탐색 수행
            else: # 유효한 상징 스펙은 없지만, 입력 시도가 있었던 경우
                 print("유효한 상징 정보가 없어 탐색을 진행하지 않습니다.")


    except ValueError:
        print("오류: 상징 개수 또는 배치 기물 수에 잘못된 숫자 형식이 입력되었습니다.")
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")