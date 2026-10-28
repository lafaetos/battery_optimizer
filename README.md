# Battery Solar Optimizer for Home Assistant

[🇺🇦 Українська](#українська) | [🇬🇧 English](#english)

---

<a name="українська"></a>
## 🇺🇦 Battery Solar Optimizer

**Battery Solar Optimizer** — це розумний кастомний компонент для Home Assistant, створений для автоматичного розрахунку оптимального рівня зарядки акумулятора вночі (за дешевим тарифом) з урахуванням прогнозу сонячної генерації (Solcast) та вашого реального енергоспоживання.

### 🎯 Навіщо потрібен цей плагін?
Якщо ви маєте гібридний інвертор, домашню батарею та сонячні панелі, перед вами часто постає питання: *«До якого рівня зарядити батарею вночі, щоб і повністю використати завтрашнє сонце, і не залишитися без світла вранці?»*

Цей алгоритм автоматично адаптується під ваші звички та погоду:
- **Адаптивне споживання з персистентністю:** Аналізує погодинне енергоспоживання будинку окремо для **робочих днів** та **вихідних** за допомогою алгоритму експоненційного згладжування (EMA). 
- **Динамічний поріг сонячного дня (Auto / Manual):** Визначення сонячного вікна (початку та кінця ефективної генерації) спирається на поріг потужності генерації. Ви можете обрати **автоматичний розрахунок** (середньогодинне споживання вашого будинку) або задати **власний поріг** (за замовчуванням `0.5 кВт`).
- **Швидкий старт та адаптація:** Щоб не чекати довго на збір статистики, ви можете або вручну вписати типові показники по годинах у файл сховища `.storage/battery_optimizer_history`, або встановити невелике значення `history_days` (наприклад, `2` дні) на початку для швидкого збору базових даних, а згодом збільшити його для стабільнішої довгострокової адаптації.
- **Інтеграція з Solcast:** Автоматично аналізує погодинний деталізований прогноз Solcast, визначаючи вікно генерації, у яке сонце дійсно покриває споживання будинку та заряджає акумулятор.
- **Фіксація заряду на кінець сонячного дня:** Автоматично фіксує та зберігає в історію реальний рівень заряду акумулятора ($SoC$) у годину закінчення сонячної генерації для подальшого аналізу дефіциту та використання цього значення в автоматизаціях.
- **Гнучкі режими роботи:**
  * *Max 100% Charge (Зима):* Розраховує необхідний нічний дозаряд з урахуванням покриття денних потреб будинку сонячною генерацією та заданою похибкою (намагається тримати заряд батареї на рівні 100%).
  * *Max Solar Utilization (Літо):* Зберігає резерв лише на ранок і мінімальний $SoC$, щоб дати сонячним панелям максимально зарядити батарею вдень.

---

### ⚙️ Параметри налаштування
Для коректної роботи потрібно налаштувати наступні параметри:

| Параметр | Назва в інтерфейсі | Опис |
| :--- | :--- | :--- |
| `consumption_sensor` | Home Energy Consumption Sensor (kWh) | Ваш лічильник накопичувальної енергії будинку в кВт·год. |
| `solcast_today_sensor` | Solcast Forecast Sensor (TODAY) | Сенсор Solcast із прогнозом генерації енергії на **сьогодні**. |
| `solcast_tomorrow_sensor` | Solcast Forecast Sensor (TOMORROW) | Сенсор Solcast із прогнозом генерації енергії на **завтра**. |
| `battery_soc_sensor` | Battery SoC Sensor (%) | Сенсор поточного рівня заряду вашого акумулятора (у %). |
| `battery_capacity_kwh` | Battery Capacity (kWh) | Повна ємність вашого акумулятора в кВт·год. |
| `min_soc` | Minimum State of Charge (%) | Мінімальний допустимий рівень розряду батареї (у відсотках). |
| `soc_offset` | Night Charge Offset (%) | Бажана похибка/зміщення нічного заряду (наприклад, `+10%` до розрахунку). |
| `history_days` | History Depth for Analysis (Days) | Кількість днів для аналізу звичок споживання (впливає на згладжування EMA). |
| `solar_threshold_mode` | Solar Threshold Mode | Режим визначення порогу генерації: `Auto (Daily Avg / 24)` або `Manual`. |
| `solar_threshold_custom` | Custom Solar Generation Threshold (kW) | Поріг визначення сонячної генерації у ручному режимі (в кВт, за замовчуванням `0.5 kW`). |
| `night_start` | Night Tariff Start Time | Час початку нічного тарифу (наприклад, `23:00`). |
| `night_end` | Night Tariff End Time | Час закінчення нічного тарифу (наприклад, `05:00`). |
| `operation_mode` | Operation Mode | Режим роботи: `Max 100% Charge (Winter)` або `Max Solar Utilization (Summer)`. |

---

### 📊 Створені сенсори (Observability)
Інтеграція створює повний набір сенсорів для моніторингу та побудови автоматизацій:
- `sensor.target_battery_soc_night` — цільовий відсоток заряду на ніч (%).
- `sensor.target_battery_energy_night` — необхідна ємність на ніч (kWh).
- `sensor.morning_consumption_forecast` — прогнозоване споживання будинку в ранковий період (kWh) (від закінчення нічного тарифу до початку генерації).
- `sensor.day_consumption_forecast` — прогнозоване споживання будинку в години сонячного дня (kWh) (від початку генерації і до кінця генерації).
- `sensor.workday_morning_consumption` / `sensor.workday_day_consumption` — ранкове та денне споживання для робочих днів (kWh).
- `sensor.weekend_morning_consumption` / `sensor.weekend_day_consumption` — ранкове та денне споживання для вихідних днів (kWh).
- `sensor.battery_soc_at_solar_end` — зафіксований рівень заряду батареї в момент закінчення сонячної генерації (%).
- `sensor.solar_generation_threshold` — поточне значення порогу сонячної генерації (kW).
- `sensor.forecasted_energy_surplus` — прогнозований надлишок енергії (kWh).
- `sensor.realtime_energy_surplus` — поточний реальний надлишок потужності (kW).
- `sensor.night_tariff_start_time` / `sensor.night_tariff_end_time` — час нічного тарифу.
- `sensor.solar_generation_start` / `sensor.solar_generation_end` — розрахований час початку та закінчення сонячної генерації.

---

### 💡 Порада: Як прискорити збір статистики споживання
За замовчуванням інтеграція використовує дефолтне значення `0.5 кВт·год` на кожну годину, доки не накопичить реальну статистику. Ви можете прискорити цей процес двома шляхами:
- **Ручне заповнення:** Перейдіть до папки `.storage` у вашому Home Assistant і відкрийте файл **`battery_optimizer_history`**. У масивах `"workday"` та `"weekend"` перелічено 24 значення, де ви можете замінити `0.5` на свої реальні середні витрати енергії по годинах. Збережіть файл і перезавантажте інтеграцію.
або
- **Тимчасове зменшення вікна історії:** Встановіть параметр `history_days` на невелике значення (наприклад, `2` дні), щоб алгоритм швидше адаптувався до поточного споживання, а через кілька днів збільште його назад для більш плавної і стабільної довгострокової адаптації.


<a name="english"></a>
## 🇬🇧 Battery Solar Optimizer

**Battery Solar Optimizer** is a smart custom component for Home Assistant designed to automatically calculate the optimal nighttime battery charge level (during cheap tariff hours) based on Solcast solar generation forecasts and your actual home energy consumption.

### 🎯 Why do you need this plugin?
If you own a hybrid inverter, home battery storage, and solar panels, you often face the question: *“What charge level should I set for the battery at night to fully utilize tomorrow's solar energy while ensuring I don't run out of power in the morning?”*

This built-in algorithm automatically adapts to your habits and the weather:
- **Persistent Adaptive Consumption:** Analyzes hourly home energy consumption separately for **workdays** and **weekends** using an Exponential Moving Average (EMA) smoothing algorithm.
- **Dynamic Solar Threshold (Auto / Manual):** Solar production windows (start and end of effective generation) are filtered using a configurable threshold. Choose **Automatic mode** (daily total / 24) or specify a **Manual threshold** (defaults to `0.5 kW`).
- **Quick Start and Fast Adaptation:** To avoid waiting for statistics to accumulate, you can either manually inject your typical hourly consumption values directly into `.storage/battery_optimizer_history`, or temporarily set `history_days` to a lower value (e.g., `2` days) for rapid initial adaptation, and increase it back later for long-term stability.
- **Solcast Integration:** Analyzes Solcast detailed hourly forecasts to filter effective solar generation hours where production covers base loads and actively charges the battery.
- **Solar End Battery SoC Capture:** Automatically records and persists the actual battery State of Charge ($SoC$) at the exact end hour of solar generation into long-term storage for deficit analysis and home automations.
- **Flexible Operating Modes:**
  * *Max 100% Charge (Winter):* Calculates required night charging while accounting for daytime solar offset of home consumption and custom safety offsets (aiming to keep the battery charged at 100%).
  * *Max Solar Utilization (Summer):* Keeps only morning headroom plus minimum $SoC$ to maximize solar self-consumption.

---

### ⚙️ Configuration Parameters
The following parameters must be configured for correct operation:

| Parameter | UI Label | Description |
| :--- | :--- | :--- |
| `consumption_sensor` | Home Energy Consumption Sensor (kWh) | Your cumulative home energy consumption sensor in kWh. |
| `solcast_today_sensor` | Solcast Forecast Sensor (TODAY) | Solcast forecast sensor for **today**. |
| `solcast_tomorrow_sensor` | Solcast Forecast Sensor (TOMORROW) | Solcast forecast sensor for **tomorrow**. |
| `battery_soc_sensor` | Battery SoC Sensor (%) | Sensor tracking your current battery state of charge (%). |
| `battery_capacity_kwh` | Battery Capacity (kWh) | Total capacity of your battery storage in kWh. |
| `min_soc` | Minimum State of Charge (%) | Minimum target state of charge percentage allowed for the battery. |
| `soc_offset` | Night Charge Offset (%) | Desired offset added to the night charge calculation (e.g., `+10%`). |
| `history_days` | History Depth for Analysis (Days) | Number of days used to analyze consumption habits (drives EMA smoothing). |
| `solar_threshold_mode` | Solar Threshold Mode | Solar generation filtering mode: `Auto (Daily Avg / 24)` or `Manual`. |
| `solar_threshold_custom` | Custom Solar Generation Threshold (kW) | Solar generation power threshold in Manual mode (in kW, default `0.5 kW`). |
| `night_start` | Night Tariff Start Time | Start time of your cheap night electricity tariff (e.g., `23:00`). |
| `night_end` | Night Tariff End Time | End time of your cheap night electricity tariff (e.g., `05:00`). |
| `operation_mode` | Operation Mode | Operating strategy: `Max 100% Charge (Winter)` or `Max Solar Utilization (Summer)`. |

---

### 📊 Exposed Sensors (Observability)
The integration creates a comprehensive set of sensors for monitoring and automations:
- `sensor.target_battery_soc_night` — target battery charge percentage for the night (%).
- `sensor.target_battery_energy_night` — required energy capacity for the night (kWh).
- `sensor.morning_consumption_forecast` — forecasted home consumption during the morning period (kWh) (from night tariff end to generation start).
- `sensor.day_consumption_forecast` — forecasted home consumption during solar hours (kWh) (from generation start to generation end).
- `sensor.workday_morning_consumption` / `sensor.workday_day_consumption` — morning and day consumption forecasts for workdays (kWh).
- `sensor.weekend_morning_consumption` / `sensor.weekend_day_consumption` — morning and day consumption forecasts for weekends (kWh).
- `sensor.battery_soc_at_solar_end` — captured battery SoC at the end of solar generation (%).
- `sensor.solar_generation_threshold` — current solar generation threshold value (kW).
- `sensor.forecasted_energy_surplus` — forecasted energy surplus (kWh).
- `sensor.realtime_energy_surplus` — real-time power surplus (kW).
- `sensor.night_tariff_start_time` / `sensor.night_tariff_end_time` — night tariff schedule.
- `sensor.solar_generation_start` / `sensor.solar_generation_end` — calculated solar generation start and end times.

---

### 💡 Tip: How to Speed Up Consumption Statistics Collection
By default, the integration uses a default value of `0.5 kWh` for each hour until real statistics are collected. You can speed up this process in two ways:
- **Manual Override:** Navigate to the `.storage` directory in your Home Assistant and open the **`battery_optimizer_history`** file. Replace the `0.5` entries in the `"workday"` and `"weekend"` arrays with your actual hourly energy usage. Save the file and reload the integration.
- **Temporary Short History Window:** Set the `history_days` parameter to a smaller value (e.g., `2` days) to quickly adapt to your current consumption pattern, and increase it back after a couple of days for steady long-term smoothing.

- Full localization support (English and Ukrainian).
- HACS compatible.
