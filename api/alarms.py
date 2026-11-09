"""Protocol v1.2 advisory rules. NO actuator, feeding, dosing or messaging I/O."""
from .configuration import values

# Basis conversion is stoichiometry, CALC; protocol itself does not name kit basis.
ION_TO_N = {"nitrite_mg_L": 14.0067 / 46.0055, "nitrate_mg_L": 14.0067 / 62.0049}

def evaluate(c, req):
    t = values(c["alarms"])
    events, unknowns = [], []
    def event(code,severity,actions):
        events.append({"code":code,"severity":severity,"actions":actions})
    required = ["pH","TAN_mg_L","nitrite_mg_L","nitrate_mg_L","KH_mg_L","DO_mg_L",
                "water_levels_pct","vermi_moisture_pct","vermi_temp_F","SOC_pct","power_ok","heartbeat_age_seconds"]
    for name in required:
        val = getattr(req, name)
        if val is None or val == {}:
            unknowns.append(name)
    if req.pH is not None and (req.pH < t['pH_alarm_low'] or req.pH > t['pH_alarm_high']):
        event('pH','ALARM',['Check KH first; spot-test, correct manually and log'])
    if req.TAN_mg_L is not None and req.TAN_mg_L >= t['TAN_alarm_mg_L']:
        event('TAN','ALARM',['Flag feeding stop; manual confirmation required','Check DO/pH/KH; log'])
    for name, threshold, code in [('nitrite_mg_L','nitrite_alarm_mg_L','nitrite'),('nitrate_mg_L','nitrate_alarm_mg_L','nitrate')]:
        val = getattr(req,name)
        if val is None: continue
        if req.nutrient_basis is None or req.protocol_nutrient_basis is None:
            unknowns.append(name+'_reporting_basis')
            continue
        if req.nutrient_basis != req.protocol_nutrient_basis:
            val = val*ION_TO_N[name] if req.nutrient_basis == 'ion' else val/ION_TO_N[name]
        exceeds = val >= t[threshold] if code == 'nitrite' else val > t[threshold]
        if exceeds:
            event(code,'ALARM',['Flag feeding stop; manual confirmation required','Log and spot-test'] if code=='nitrite' else ['Review plant load/feeding manually; cross-check N model; log'])
    if req.KH_mg_L is not None and req.KH_mg_L < t['KH_alarm_mg_L']:
        event('KH','ALARM',['KH in mg/L CaCO3 only: review bicarbonate addition manually; log'])
    if req.DO_mg_L is not None:
        if req.DO_mg_L <= t['DO_critical_mg_L']:
            event('DO','CRITICAL',['Force backup aeration; shed non-critical loads','Aeration and core circulation must keep running; log'])
        elif req.DO_mg_L <= t['DO_warning_mg_L']:
            event('DO','WARNING',['Backup aeration on; log'])
    levels = req.water_levels_pct or {}
    for vessel in ['fish_tank','sump']:
        if vessel not in levels: unknowns.append('water_levels_pct.'+vessel)
    for vessel,level in levels.items():
        if level <= t['level_critical_pct']:
            event('level:'+vessel,'CRITICAL',['Stop non-critical pumps only','Keep core circulation and aeration on backup power','Dry-run risk requires hard alarm and manual confirmation before ANY core circulation stop; aeration never stops'])
        elif level <= t['level_low_pct']:
            event('level:'+vessel,'ALARM',['Stop non-critical pumps only; escalate backup power','Do NOT auto-stop core circulation or aeration; log'])
    if req.circulation_dry_run_risk:
        event('dry_run','CRITICAL',['Hard alarm; manual confirmation required before any circulation stop','Aeration never stops'])
    if req.vermi_moisture_pct is not None and not t['vermi_moisture_low_pct'] <= req.vermi_moisture_pct <= t['vermi_moisture_high_pct']:
        event('vermi_moisture','ALARM',['Adjust watering manually; log'])
    if req.vermi_temp_F is not None and (req.vermi_temp_F < t['vermi_temp_low_F'] or req.vermi_temp_F > t['vermi_temp_high_F']):
        event('vermi_temperature','ALARM',['Shade/insulate/heat as appropriate; log'])
    if req.SOC_pct is not None and req.SOC_pct <= t['SOC_floor_pct']:
        event('SOC','ALARM',['Shed non-critical loads only; protect circulation and aeration'])
    if req.power_ok is False:
        event('power','CRITICAL',['Force backup aeration; escalate backup power; shed non-critical loads'])
    ages = req.heartbeat_age_seconds or {}
    if req.expected_sensor_ids is None or not req.expected_sensor_ids:
        unknowns.append('expected_sensor_ids (critical sensor inventory not configured)')
    for sensor in req.expected_sensor_ids or []:
        if sensor not in ages:
            event('heartbeat:'+sensor,'FAIL',['Missing critical-sensor heartbeat; parameter FAIL, alarm and log'])
    for sensor,age in ages.items():
        if age >= t['heartbeat_seconds']:
            event('heartbeat:'+sensor,'FAIL',['One missed critical-sensor heartbeat; parameter FAIL, alarm and log'])
    if req.ro_active:
        for k in ['ro_recovery_pct','ro_TDS_ppm']:
            if getattr(req,k) is None:unknowns.append(k)
        if req.ro_recovery_pct is not None and req.ro_recovery_pct < t['ro_min_recovery_pct']:
            event('RO_recovery','ALARM',['Stop RO feed; log; inspect membrane/prefilter (historical protocol requirement, not a pilot performance guarantee)'])
        if req.ro_TDS_ppm is not None and req.ro_TDS_ppm >= t['ro_max_TDS_ppm']:
            event('RO_TDS','ALARM',['Divert permeate; stop RO; log'])
    status = 'CRITICAL' if any(e['severity']=='CRITICAL' for e in events) else ('FAIL' if any(e['severity']=='FAIL' for e in events) else ('ALARM' if any(e['severity']=='ALARM' for e in events) else ('WARNING' if events else ('INCOMPLETE' if unknowns else 'NO_THRESHOLD_BREACH'))))
    return {'label':'CALC','source':'measurement-protocol-v1.md v1.2 §4–§5; thresholds are QUOTED user-confirmed literature bounds, not field validated',
            'status':status,'evaluation_complete':not unknowns,'events':events,'missing_or_unconfirmed':unknowns,
            'data_label':req.data_label,'data_source':req.data_source,
            'nutrient_basis':req.nutrient_basis,'protocol_nutrient_basis':req.protocol_nutrient_basis,
            'basis_note':'Protocol NO2/NO3 basis is unconfirmed. Both bases must be explicitly asserted; conversions use molecular weights (CALC).',
            'control_mode':'ADVISORY ONLY: no device actions, dosing, feeding, external notifications or automatic hardware stops executed',
            'thresholds':c['alarms']}
