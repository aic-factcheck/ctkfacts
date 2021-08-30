import json
import os
import random
import urllib.parse
import urllib.request
from datetime import datetime
import unicodedata as ud

from sentence_transformers import InputExample
from sklearn.model_selection import train_test_split

#  The id's that were used in the first three "hacky" iterations of this scheme
PREVIOUSLY_USED = frozenset((4098, 4099, 4102, 7, 2058, 2060, 4110, 4112, 4114, 2067, 4118, 2071, 28, 29, 4126, 4129, 2083, 39, 4137, 4139, 2092, 2093, 2094, 4141, 4140, 2097, 2091, 2100, 4148, 4149, 4153, 4154, 2107, 60, 2112, 4160, 66, 2114, 67, 69, 70, 71, 72, 2120, 2122, 2123, 4170, 4173, 2126, 79, 2129, 82, 83, 4182, 87, 89, 94, 2142, 2143, 2145, 4194, 2152, 4202, 2154, 108, 4209, 115, 116, 2165, 2167, 4216, 4217, 122, 2171, 2173, 126, 4223, 2177, 4227, 134, 135, 138, 139, 2187, 4236, 140, 146, 147, 2195, 149, 2197, 152, 153, 154, 4251, 2204, 157, 4254, 159, 4256, 2207, 4258, 161, 4261, 4265, 2218, 4266, 170, 4269, 4270, 4271, 4272, 4276, 2229, 4277, 2228, 4280, 2233, 186, 2234, 4281, 4282, 4283, 2239, 4284, 4285, 2242, 4288, 4289, 197, 198, 2238, 196, 200, 202, 201, 4294, 2254, 208, 209, 4306, 4304, 2259, 2261, 4310, 2257, 4311, 4313, 2266, 222, 2272, 225, 226, 2275, 4326, 4327, 4329, 234, 235, 4331, 237, 4332, 236, 240, 2281, 4338, 243, 2291, 239, 4342, 2295, 4343, 2296, 2298, 4346, 2303, 256, 4353, 4355, 260, 2309, 262, 263, 264, 4363, 4364, 270, 2318, 4367, 4368, 274, 2323, 2324, 276, 280, 282, 283, 4380, 2334, 4383, 2337, 4386, 291, 4389, 4392, 298, 4394, 4396, 300, 301, 4402, 4403, 4404, 4407, 4409, 2363, 4412, 2365, 4414, 4416, 4419, 2372, 4421, 326, 2375, 2374, 330, 2378, 4426, 2379, 2382, 2383, 333, 337, 2385, 2388, 2389, 4438, 2390, 4440, 4437, 2394, 4442, 340, 349, 2397, 4447, 352, 4449, 350, 4451, 2405, 358, 4455, 360, 4457, 2410, 4459, 2407, 4456, 2412, 367, 368, 4465, 2418, 371, 4466, 373, 4469, 4463, 2421, 2425, 378, 4474, 4476, 2430, 383, 385, 2433, 2438, 392, 394, 395, 2443, 2442, 400, 2449, 2451, 2452, 2453, 408, 409, 2456, 411, 2459, 412, 2462, 2463, 2461, 418, 419, 2466, 2469, 2474, 428, 429, 432, 433, 434, 436, 437, 441, 444, 2494, 2497, 2498, 451, 450, 455, 2503, 457, 462, 463, 2516, 469, 472, 2520, 2521, 2525, 481, 2530, 483, 484, 487, 2538, 2544, 500, 2549, 2550, 505, 506, 508, 2558, 2559, 510, 514, 518, 519, 520, 521, 522, 2569, 2571, 2573, 2578, 534, 2583, 536, 537, 2584, 2585, 2587, 542, 545, 546, 2595, 2596, 2597, 2600, 556, 558, 2607, 560, 2608, 2613, 570, 2618, 571, 2621, 574, 2625, 2627, 2628, 582, 2632, 585, 586, 2635, 598, 2646, 600, 605, 607, 610, 2658, 2659, 616, 2664, 2666, 623, 624, 2672, 2676, 2678, 2679, 2680, 634, 639, 2687, 2688, 647, 2695, 651, 653, 2703, 657, 659, 661, 2710, 663, 2711, 666, 2715, 2716, 2717, 671, 2719, 2721, 675, 2725, 682, 2730, 684, 687, 689, 2737, 690, 2742, 2743, 2744, 2753, 2754, 711, 2759, 713, 2761, 715, 2766, 2767, 720, 2769, 2770, 723, 725, 2775, 2776, 2777, 2778, 730, 729, 733, 735, 737, 2786, 740, 741, 2792, 2795, 2796, 2797, 750, 751, 756, 2806, 2810, 768, 769, 770, 2819, 779, 780, 2829, 2834, 790, 792, 794, 795, 2842, 2846, 2847, 804, 2852, 2858, 818, 820, 822, 823, 824, 825, 828, 829, 2877, 833, 838, 2890, 2891, 2900, 2902, 2903, 2907, 2908, 860, 2915, 2917, 2921, 874, 2923, 2925, 878, 881, 882, 2932, 886, 2935, 889, 2938, 895, 897, 2945, 2951, 904, 2954, 908, 2957, 912, 2961, 2966, 921, 922, 923, 2972, 928, 2979, 2980, 185, 2983, 940, 187, 942, 2993, 2994, 2995, 2996, 2997, 950, 2999, 3000, 947, 957, 958, 3005, 3006, 960, 3011, 3012, 3013, 967, 3018, 3022, 3023, 976, 3029, 982, 983, 3032, 3034, 989, 2232, 992, 997, 3052, 3053, 1006, 3055, 1008, 3059, 3062, 3063, 1016, 1019, 3069, 3070, 3071, 1024, 3073, 3074, 3075, 3076, 1029, 1034, 1037, 3087, 1041, 1042, 1043, 3091, 3093, 3095, 3097, 3098, 1052, 3101, 3100, 3103, 3105, 3108, 3110, 3111, 3112, 3114, 3118, 1071, 1072, 1074, 3124, 3125, 1080, 3131, 4286, 1084, 3134, 1088, 3139, 1095, 3143, 1106, 1107, 3158, 3159, 3161, 1115, 1116, 3164, 3168, 1125, 1126, 3174, 3178, 3180, 3181, 1138, 1139, 1140, 1141, 1142, 1144, 1148, 1149, 3197, 1150, 1155, 3205, 1158, 1160, 1162, 1163, 3211, 3212, 3214, 3217, 1170, 3219, 1174, 1177, 3225, 1178, 1181, 3232, 3233, 3234, 3235, 1189, 1190, 3237, 3238, 1191, 3246, 1199, 3247, 1204, 3252, 1206, 3255, 3256, 1212, 3261, 1215, 3266, 1220, 3273, 1226, 1225, 1228, 3277, 3278, 3276, 1233, 1235, 3285, 3286, 1239, 3288, 3289, 3290, 1243, 3292, 3291, 1246, 3295, 3296, 1248, 3302, 3304, 3305, 3306, 1259, 3308, 1261, 3310, 3311, 3312, 1268, 1270, 3320, 3321, 1274, 1278, 3327, 1284, 3338, 1297, 3345, 3347, 3350, 3351, 1304, 3352, 1306, 3354, 3358, 1313, 1315, 1316, 3365, 3373, 3379, 3381, 3382, 1338, 3386, 3388, 3387, 3391, 1344, 3393, 1346, 3392, 1350, 3399, 3400, 1353, 3398, 3403, 1352, 1359, 1361, 1362, 1365, 1366, 3413, 3415, 1367, 3421, 3423, 1379, 1382, 1385, 1388, 3441, 3442, 1395, 1396, 3445, 3444, 1399, 1400, 1397, 3450, 1409, 1410, 1411, 3458, 1413, 3459, 1414, 1423, 3471, 3476, 3478, 3487, 1442, 1444, 1446, 1447, 3494, 1451, 3500, 1453, 3501, 3523, 1475, 1476, 3529, 3530, 1488, 3541, 3542, 3544, 3545, 3548, 3549, 1504, 1505, 3552, 3553, 1508, 1509, 1510, 3559, 1511, 1512, 3564, 3567, 3569, 1522, 3570, 3572, 1523, 1525, 3575, 3576, 1521, 3581, 1534, 3584, 3585, 3588, 1541, 1542, 1543, 3591, 1547, 3598, 1554, 3602, 1556, 3605, 3603, 3609, 3610, 1565, 3615, 1568, 1567, 1570, 3620, 3621, 1574, 1575, 1578, 3631, 3633, 3638, 1593, 1597, 1599, 3649, 3652, 3654, 1610, 1612, 1623, 1624, 3676, 3677, 1630, 1632, 1634, 3687, 1639, 3688, 1651, 3703, 3704, 3705, 1655, 3707, 1660, 1663, 1666, 3717, 3718, 1671, 3720, 3721, 1676, 1677, 3727, 1683, 3738, 1691, 3740, 1695, 3744, 3745, 3747, 3748, 1704, 3755, 1707, 3759, 3764, 1720, 3769, 1723, 1724, 3775, 3779, 1732, 1733, 3782, 3781, 1739, 1744, 3798, 1751, 1752, 1755, 3806, 3808, 1761, 1762, 3812, 1769, 1772, 3821, 3820, 3823, 3824, 1779, 3831, 1784, 3833, 1783, 3837, 3839, 1794, 1795, 3844, 3845, 357, 3850, 3852, 1804, 1807, 3855, 3856, 3857, 1817, 1818, 1821, 1825, 3874, 3875, 3876, 3877, 1830, 1828, 3878, 1833, 1834, 1835, 365, 1839, 3889, 3892, 1850, 1851, 1853, 1856, 1857, 1862, 3912, 1873, 3923, 1876, 1878, 3936, 3940, 3942, 3943, 1897, 1898, 1900, 1906, 3955, 3956, 3959, 3962, 1916, 3965, 1924, 1927, 1930, 3985, 1939, 1942, 1944, 3993, 3996, 1952, 1955, 1956, 4004, 1957, 4003, 4010, 4012, 1966, 1968, 1970, 1971, 4462, 1973, 1975, 1981, 4029, 1983, 4034, 4039, 4040, 1993, 4042, 4044, 4049, 2005, 2006, 4055, 2008, 4061, 2015, 2016, 4064, 4066, 2024, 4076, 2031, 4081, 4084, 2039, 4093))
LABEL_NUM = {"SUPPORTS":0, "REFUTES": 1, "NOT ENOUGH INFO":2}
LABEL_STR = {0: "SUPPORTS", 1: "REFUTES", 2: "NOT ENOUGH INFO"}

def load_api_export(format="nli", evidence_format="text", simulate_nei_evidence=1, single_evidence=0):
    params = {
        "format": format,
        "evidenceFormat": evidence_format,
        "simulateNeiEvidence": simulate_nei_evidence,
        "singleEvidence": single_evidence
    }
    result = []
    with urllib.request.urlopen("https://fcheck.fel.cvut.cz/label/export?" + urllib.parse.urlencode(params)) as url:
        for line in url:
            result.append(json.loads(line.decode("utf-8")))
    return result


def load_jsonl(location="../export-snapshots/export_08-27-2021_0655pm_173.jsonl"):
    with open(location, "r", encoding="utf-8") as file:
        result = []
        for line in file:
            result.append(json.loads(line))
    return result


def save_splits(train, validation, test, folder=None):
    if folder is None:
        folder = f"../data/dump{datetime.now().strftime('_%d-%m-%Y_%H-%M-%S')}"
    if not os.path.exists(folder):
        os.mkdir(folder)

    save_jsonl(train, folder+"/train.jsonl")
    save_jsonl(validation, folder+"/validation.jsonl")
    save_jsonl(test, folder+"/test.jsonl")


def save_jsonl(data, location=None):
    if location is None:
        location = f"../data/dump{datetime.now().strftime('_%d-%m-%Y_%H-%M-%S')}.jsonl"
    with open(location, "w", encoding="utf-8") as f:
        for datapoint in data:
            print(json.dumps(datapoint, ensure_ascii=False), file=f)


def expand_by_evidence(dataset):
    result, label_id = [], 1
    for datapoint in dataset:
        for evidence in datapoint["evidence"]:
            datapoint_expanded = datapoint.copy()
            datapoint_expanded["label_id"], datapoint["evidence"] = label_id, evidence
            result.append(datapoint_expanded)
        label_id += 1
    return result


def collapse_by(dataset, parameter="source"):
    result = {}
    for datapoint in dataset:
        if datapoint[parameter] not in result:
            result[datapoint[parameter]] = []
        result[datapoint[parameter]].append(datapoint)
    result = list(result.values())
    labels = []
    for collapsed in result:
        s = r = n = t = 0
        for datapoint in collapsed:
            s += datapoint["label"] == "SUPPORTS"
            r += datapoint["label"] == "REFUTES"
            n += datapoint["label"] == "NOT ENOUGH INFO"
            t += 1
        labels += ["NOT ENOUGH INFO" if max(s, r, n) == n else ("REFUTES" if max(s, r, n) == r else "SUPPORTS")]
    return result, labels


def counter(dataset):
    if "label" in dataset[0]:
        dataset = [datapoint["label"] for datapoint in dataset]
    values = sorted(list(set(dataset)))
    return [(value, dataset.count(value), dataset.count(value) / len(dataset)) for value in values]


def expand_collapsed(dataset):
    result = []
    for datapoints in dataset:
        result.extend(datapoints)
    return result


def split(dataset, test_size=.12, validation_size=.12, skip_ids=PREVIOUSLY_USED, leakage_prevention_level="source",
          seed=1234):
    skipped = [datapoint for datapoint in dataset if datapoint["id"] in skip_ids]
    dataset = [datapoint for datapoint in dataset if datapoint["id"] not in skip_ids]

    dataset, labels = collapse_by(dataset, leakage_prevention_level)

    if isinstance(test_size, float):
        test_size = int(test_size * len(dataset))
    if isinstance(validation_size, float):
        validation_size = int(validation_size * len(dataset))

    train, test, train_labels, test_labels = train_test_split(
        dataset, labels, test_size=test_size, random_state=seed, stratify=labels
    )
    train, validation, train_labels, validation_labels = train_test_split(
        train, train_labels, test_size=validation_size, random_state=seed, stratify=train_labels
    )
    train, validation, test = (expand_collapsed(d) for d in (train, validation, test))
    train.extend(skipped)
    random.Random(seed).shuffle(train)
    return train, validation, test


def to_examples(dataset, norm="NFC"):
    return [
        InputExample(
            datapoint["id"],
            [ud.normalize(" ".join(datapoint["evidence"]), norm), ud.normalize(datapoint["claim"])],
            LABEL_NUM[datapoint["label"]])
        for datapoint in dataset
    ]

#  location = "../export-snapshots/export_08-30-2021_0200am_173.jsonl"
#  dataset = load_jsonl(location)
#
#  dataset = expand_by_evidence(dataset)
#  train, validation, test = split(dataset)
#  print(counter(train), "\n", counter(validation), "\n", counter(test))
