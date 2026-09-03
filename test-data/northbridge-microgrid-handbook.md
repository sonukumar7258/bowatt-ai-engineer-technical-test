# Northbridge Community Microgrid Operations Handbook

This is a fictional document created for testing a retrieval-augmented generation system. All organizations, people, locations, equipment identifiers, measurements, and procedures in this handbook are invented. They should not be used to operate a real electrical system.

## 1. Site overview

The Northbridge Community Microgrid serves the fictional town of Northbridge Vale. The system began normal operation on 14 April 2024 after an eighteen-month construction and commissioning period. It supplies three priority facilities: Alder Community Hospital, Northbridge Water Works, and Beacon Emergency Shelter. Residential customers remain connected to the regional utility and receive microgrid support only when the site is operating in island mode.

The microgrid has three primary energy resources. The Sunfield solar array has a rated peak capacity of 4.8 megawatts. The Ridgeway wind installation contains three turbines with a combined rated capacity of 3.6 megawatts. The Willow battery energy storage system can deliver 2.5 megawatts of power and stores 7.5 megawatt-hours of usable energy. A 1.2-megawatt biodiesel generator, identified as generator BG-12, is reserved for prolonged outages and black-start support.

The normal grid connection is through the East Gate substation. The point of common coupling is breaker PCC-01. The microgrid controller is identified as NMC-4 and is installed in the operations building beside the substation. Operators monitor the system from the Northbridge Control Room, which is staffed from 06:00 to 22:00 every day. Outside those hours, the on-call operator receives alarms through the PagerOak notification service.

## 2. Operating priorities

The first operating priority is safety. No generation target, cost reduction, or service objective takes precedence over the safety of personnel or the public. The second priority is maintaining power to critical loads. Alder Community Hospital is priority level one, Northbridge Water Works is priority level two, and Beacon Emergency Shelter is priority level three. The third priority is preserving sufficient battery capacity for an unexpected grid outage.

During normal grid-connected operation, the target minimum state of charge for the Willow battery is 45 percent. Between 1 November and 31 March, the winter reserve target increases to 60 percent because storms are more frequent. The controller may allow state of charge to fall five percentage points below the applicable target for no more than fifteen minutes when smoothing a rapid change in renewable generation.

Energy may be exported to the regional utility only when the battery is above its reserve target and the next six-hour renewable forecast exceeds the expected critical-load demand by at least 20 percent. Export power is limited to 2.0 megawatts at PCC-01. If the regional utility issues a Red Finch restriction notice, all exports must stop within sixty seconds.

## 3. Battery operating rules

The Willow battery is divided logically into five equal monitoring blocks named W1 through W5. These are software groupings used for diagnostics; operators must not assume that they correspond to physical rack boundaries. The preferred operating range is 20 to 90 percent state of charge. Routine dispatch outside that range requires approval from the duty manager.

The maximum routine charge or discharge power is 2.0 megawatts. The controller may use the full 2.5-megawatt rating for up to ten minutes during islanding or frequency support. After any interval above 2.0 megawatts, the battery must remain at or below 1.5 megawatts for at least twenty minutes. This recovery period is called a Blue Rest interval.

Battery temperature is monitored at the block level. A temperature above 38 degrees Celsius creates an Amber Thermal alarm. At 42 degrees Celsius, the affected block must stop charging and its discharge power must be limited to 25 percent of normal. At 46 degrees Celsius, the controller must isolate the affected block and notify the fire-response liaison. The fictional emergency isolation switch is labeled EIS-WILLOW and is located outside the north wall of the battery building.

A state-of-charge disagreement greater than four percentage points between any two blocks triggers a Balance Review. If the disagreement persists for thirty minutes, the controller reduces total battery power to 0.8 megawatts. The restriction remains until the difference has stayed below two percentage points for one continuous hour.

## 4. Island-mode procedure

The microgrid enters island mode when PCC-01 opens and local generation continues serving selected loads. Automatic islanding is expected when grid voltage remains below 85 percent of nominal for 1.5 seconds. Operators may also initiate planned islanding during an approved utility exercise.

Immediately after islanding, NMC-4 sheds non-priority loads and confirms that Alder Community Hospital remains energized. The target system frequency is 50 hertz. The first stabilization band is 49.7 to 50.3 hertz. If frequency leaves this band for more than five seconds, the battery provides fast frequency support. If frequency falls below 49.2 hertz, Beacon Emergency Shelter may be shed temporarily, but Northbridge Water Works must remain connected unless the duty manager declares a Level Three emergency.

Within five minutes of islanding, the operator must complete the Island Status checklist. The checklist records the time PCC-01 opened, battery state of charge, active generation, connected priority loads, estimated renewable production for the next two hours, and the name of the operator. The operator then contacts the regional utility using communication channel Cedar-7.

BG-12 should start when the battery reaches 32 percent state of charge during island mode or when the two-hour forecast shows an energy deficit greater than 1.0 megawatt-hour. Once started, BG-12 should normally run at or above 40 percent of rated power. The generator should stop only after the battery has recovered to 55 percent and the two-hour forecast shows a surplus of at least 0.5 megawatt-hour.

## 5. Black-start procedure

A black start is required when the microgrid bus is de-energized and the regional grid cannot restore service. Only operators with current Black Lantern certification may lead the procedure. Certification expires every twelve months. The duty manager must record the reason for the black start and assign a second qualified operator to verify each switching step.

The sequence begins by confirming that PCC-01 is open and tagged. All renewable feeders must initially remain open. BG-12 is then started using its independent battery system. After generator voltage and frequency remain stable for two minutes, the operator energizes the essential services bus. The Willow battery inverter may then connect in grid-forming mode.

Renewable resources are restored one at a time. The Sunfield solar array is connected first in sections no larger than 1.0 megawatt. Each section requires a thirty-second observation period. Ridgeway wind generation is connected only after the battery state of charge exceeds 25 percent and system frequency has remained within 49.8 to 50.2 hertz for five minutes.

The black-start process must be paused if frequency changes faster than 0.5 hertz per second, if voltage leaves the range of 92 to 108 percent of nominal, or if communications with the second operator are lost. After a successful restoration, the lead operator files a Black Lantern report before the end of the shift.

## 6. Return to grid-connected operation

Reconnection requires permission from the regional utility. The utility issues a synchronization window over Cedar-7. Before closing PCC-01, voltage difference must be below 3 percent, frequency difference must be below 0.1 hertz, and phase-angle difference must be below 10 degrees. These conditions must remain satisfied for at least twenty seconds.

After PCC-01 closes, the microgrid remains in observation mode for fifteen minutes. Export is disabled during this period, battery power is limited to 1.0 megawatt, and operators confirm that all three priority facilities have stable supply. If PCC-01 trips again during observation mode, the system returns to island mode and the operator must not attempt another reconnection without new utility permission.

## 7. Maintenance schedule

Operators perform a visual site walk every Monday, Wednesday, and Friday before 10:00. The walk includes checking perimeter gates, listening for unusual inverter or transformer noise, checking that ventilation openings are clear, and confirming that emergency access routes are unobstructed.

The Willow battery receives a capacity verification test on the first Tuesday of January, April, July, and October. The test may be postponed by up to seven days if severe weather is forecast. BG-12 receives a twenty-minute no-load start test every Thursday at 09:30 and a loaded test on the second Thursday of each month. Fuel samples are sent for analysis twice per year.

Solar-array thermal images are collected in May and September between 11:00 and 14:00 on a mostly clear day. Ridgeway turbine vibration data is reviewed monthly. A detailed turbine inspection is scheduled every six months, with the spring inspection occurring before 15 April whenever weather permits.

Maintenance work that makes more than 1.0 megawatt of generation unavailable must be entered in the operations calendar at least five working days in advance. Emergency maintenance is exempt, but the duty manager and regional utility must be notified as soon as practical.

## 8. Alarm handling

Alarms have three operational levels. Yellow alarms indicate abnormal conditions that require review within thirty minutes. Amber alarms require operator action within ten minutes. Red alarms indicate an immediate safety or stability risk and require acknowledgement within sixty seconds.

Every alarm response follows the CLEAR sequence: Confirm the alarm, Locate the affected equipment, Evaluate current risk, Act according to the relevant procedure, and Record the result. Operators must not clear an alarm merely to silence it. If two or more Red alarms occur within a five-minute period, the duty manager is automatically called.

The PagerOak service escalates an unacknowledged Red alarm to the on-call operator after sixty seconds, to the duty manager after three minutes, and to the operations director after seven minutes. PagerOak is a notification tool only and must never issue switching commands.

## 9. Incident reporting

An operational incident is any unplanned loss of a priority load, unexpected islanding, safety-system activation, battery block isolation, failed black start, or export above the 2.0-megawatt limit. The operator creates an initial incident record within thirty minutes. The record must include known facts and must clearly separate observations from assumptions.

The incident commander assigns a severity from N1 through N4. N1 is a minor event with no service interruption. N2 involves degraded operation or a priority-three interruption shorter than ten minutes. N3 includes any interruption to Northbridge Water Works, an interruption to Beacon Emergency Shelter lasting ten minutes or more, or an unsuccessful reconnection attempt. N4 includes any interruption to Alder Community Hospital, injury, fire, or event requiring public emergency services.

N3 and N4 incidents require a review meeting within two working days. A written root-cause report is due within ten working days. Corrective actions must have an owner and target date. Closure requires evidence that each action was completed; a verbal confirmation is not sufficient.

## 10. Data retention and access

High-resolution electrical measurements are retained for ninety days. Five-minute operational averages are retained for seven years. Alarm and incident records are retained for ten years. Training records are retained for five years after a person's access authorization ends.

Operators authenticate to NMC-4 with an individual account and a hardware security key. Shared accounts are prohibited. Temporary vendor access requires a named sponsor, expires after eight hours, and permits read-only access unless the duty manager approves a specific maintenance window.

Configuration changes are recorded in the Copper Ledger. Each entry includes the change identifier, affected equipment, reason, person making the change, reviewer, test evidence, and rollback method. Emergency changes may be applied before review, but they must be entered in the Copper Ledger within four hours and reviewed by the next working day.

## 11. Training and drills

New operators complete supervised training before receiving independent control-room access. Required modules cover electrical safety, battery hazards, island operation, alarm response, incident reporting, and communication with the regional utility. Operators must pass each module with a score of at least 80 percent.

The team conducts an islanding drill every three months and a tabletop black-start exercise every six months. One full black-start drill is conducted each year during a utility-approved window. The annual drill must include a simulated loss of one communication channel and a handover between operators.

The fictional training coordinator, Mira Solberg, maintains the drill calendar. The duty manager, Tomas Reed, approves Black Lantern certification. Questions about PagerOak escalation rules go to the operations-support lead, Imani Vale.

## 12. Quick-reference values

- Solar capacity: 4.8 megawatts.
- Wind capacity: 3.6 megawatts.
- Battery rating: 2.5 megawatts and 7.5 megawatt-hours.
- Biodiesel generator rating: 1.2 megawatts.
- Normal battery reserve target: 45 percent.
- Winter battery reserve target: 60 percent.
- Battery start threshold for BG-12 in island mode: 32 percent.
- Battery recovery threshold before stopping BG-12: 55 percent.
- Maximum export at PCC-01: 2.0 megawatts.
- Normal frequency target: 50 hertz.
- Red alarm acknowledgement target: sixty seconds.
- Control-room staffed hours: 06:00 to 22:00.

## 13. Deliberately unanswerable details

This handbook does not state the purchase price of the Willow battery, the street address of Alder Community Hospital, the names of residential customers, or the serial number of PCC-01. A research system grounded only in this document should say that these details are not provided rather than inventing an answer.
