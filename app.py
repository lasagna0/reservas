import pandas as pd
import streamlit as st
import datetime as dt
import sqlite3

today = dt.date.today()

# Database setup
conn = sqlite3.connect('salas.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS salas
                ([id] INTEGER PRIMARY KEY,[name] text)''')
c.execute('''CREATE TABLE IF NOT EXISTS reservas
                ([id] INTEGER PRIMARY KEY,[sala_id] INTEGER, [fecha] string, [hora_inicio] time, [hora_fin] time, [nombre_reservante] text, [email_reservante] text, [invitados] text, [motivo] text, [observaciones] text)''')
conn.commit()

st.title('Sistema de reserva de salas')
st.write('Mediante este aplicativo podrás verificar la disponibilidad y reservar salas de reuniones en la oficina de la empresa')

st.sidebar.header('Selecciona una sala')

# Select sala
sala = st.sidebar.selectbox('Sala', ['General', 'Manglar 1', 'Manglar 2', 'Manglares', 'Rio', 'Mar'])

# Function to find available sala
def find_available_sala(sala_id, day):
    reservation_df = pd.read_sql_query(f"SELECT * FROM reservas WHERE sala_id={sala_id} AND fecha='{day}'", conn)

    list_of_availability = []
    if reservation_df.empty:
        # If there are no reservations, the sala is available from 7am to 8pm
        list_of_availability.append(('07:00:00', '20:00:00'))
    else:
        # If there are reservations, the sala is available from 7am to the first reservation start time
        first_reservation_start = reservation_df['hora_inicio'].iloc[0]
        if first_reservation_start != '07:00:00':
            list_of_availability.append(('07:00:00', first_reservation_start))

        # Add available time chunks between reservations
        for i in range(len(reservation_df) - 1):
            end_time = reservation_df['hora_fin'].iloc[i]
            start_time = reservation_df['hora_inicio'].iloc[i + 1]
            if end_time != start_time:
                list_of_availability.append((end_time, start_time))

        # Add available time chunk after the last reservation
        last_reservation_end = reservation_df['hora_fin'].iloc[-1]
        if last_reservation_end != '20:00:00':
            list_of_availability.append((last_reservation_end, '20:00:00'))

    return list_of_availability

if sala == 'General':
    st.write('Selecciona una sala de reuniones para ver su disponibilidad')
    st.subheader('Disponibilidad de hoy')
    col1, col2, col3, col4, col5 = st.columns(5)

    # Get availability for each sala
    for i, col in enumerate([col1, col2, col3, col4, col5], 1):
        with col:
            st.subheader(f'Sala {i}')
            list_of_availability = find_available_sala(i, str(today))
            st.write("Disponible entre:")
            for start_time, end_time in list_of_availability:
                st.write(f"{start_time} - {end_time}")
elif sala in ['Manglar 1', 'Manglar 2']:
    st.write(f'Estás a punto de reservar {sala}')
    selected_date = st.date_input('Selecciona una fecha', today, key='date')

    list_of_availability = find_available_sala(1, str(selected_date))
    st.write("Disponible entre:")
    for start_time, end_time in list_of_availability:
        st.write(f"{start_time} - {end_time}")

    selected_start_time = st.time_input('Selecciona una hora de inicio para tu reserva', key='start_time')
    selected_end_time = st.time_input('Selecciona una hora de fin para tu reserva', key='end_time')

    name = st.text_input('Ingresa tu nombre', key='name')
    email = st.text_input('Ingresa tu email', key='email')
    guests = st.text_input('Ingresa los nombres de tus invitados', key='guests')
    reason = st.text_input('Ingresa el motivo de la reunión', key='reason')
    observations = st.text_input('Ingresa observaciones', key='observations')

    if st.button('Reservar'):
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        c.execute("INSERT INTO reservas (sala_id, fecha, hora_inicio, hora_fin, nombre_reservante, email_reservante, invitados, motivo, observaciones) VALUES (?,?,?,?,?,?,?,?,?)",
                  (1, selected_date_str, selected_start_time, selected_end_time, name, email, guests, reason, observations))
        conn.commit()
        st.write('Tu reserva ha sido exitosa')
        st.write('Tu reserva es para el día:', selected_date_str)
        st.write('Desde las:', selected_start_time)
        st.write('Hasta las:', selected_end_time)

elif sala == 'Manglares':
    st.write('Estás a punto de reservar Manglares (Manglar 1 y Manglar 2)')
    selected_date = st.date_input('Selecciona una fecha', today, key='date')

    list_of_availability_manglar1 = find_available_sala(2, str(selected_date))
    list_of_availability_manglar2 = find_available_sala(3, str(selected_date))

    st.write("Disponibilidad de Manglar 1:")
    for start_time, end_time in list_of_availability_manglar1:
        st.write(f"{start_time} - {end_time}")

    st.write("Disponibilidad de Manglar 2:")
    for start_time, end_time in list_of_availability_manglar2:
        st.write(f"{start_time} - {end_time}")

    selected_start_time = st.time_input('Selecciona una hora de inicio para tu reserva', key='start_time')
    selected_end_time = st.time_input('Selecciona una hora de fin para tu reserva', key='end_time')

    name = st.text_input('Ingresa tu nombre', key='name')
    email = st.text_input('Ingresa tu email', key='email')
    guests = st.text_input('Ingresa los nombres de tus invitados', key='guests')
    reason = st.text_input('Ingresa el motivo de la reunión', key='reason')
    observations = st.text_input('Ingresa observaciones', key='observations')

    if st.button('Reservar'):
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        c.execute("INSERT INTO reservas (sala_id, fecha, hora_inicio, hora_fin, nombre_reservante, email_reservante, invitados, motivo, observaciones) VALUES (?,?,?,?,?,?,?,?,?)",
                  (2, selected_date_str, selected_start_time, selected_end_time, name, email, guests, reason, observations))
        c.execute("INSERT INTO reservas (sala_id, fecha, hora_inicio, hora_fin, nombre_reservante, email_reservante, invitados, motivo, observaciones) VALUES (?,?,?,?,?,?,?,?,?)",
                  (3, selected_date_str, selected_start_time, selected_end_time, name, email, guests, reason, observations))
        conn.commit()
        st.write('Tu reserva ha sido exitosa')
        st.write('Tu reserva es para el día:', selected_date_str)
        st.write('Desde las:', selected_start_time)
        st.write('Hasta las:', selected_end_time)

elif sala == 'Rio':
    #add code for Rio
    st.write('Estás a punto de reservar Rio')
    selected_date = st.date_input('Selecciona una fecha', today, key='date')

    list_of_availability = find_available_sala(4, str(selected_date))
    st.write("Disponible entre:")
    for start_time, end_time in list_of_availability:
        st.write(f"{start_time} - {end_time}")

    selected_start_time = st.time_input('Selecciona una hora de inicio para tu reserva', key='start_time')
    selected_end_time = st.time_input('Selecciona una hora de fin para tu reserva', key='end_time')

    name = st.text_input('Ingresa tu nombre', key='name')
    email = st.text_input('Ingresa tu email', key='email')
    guests = st.text_input('Ingresa los nombres de tus invitados', key='guests')
    reason = st.text_input('Ingresa el motivo de la reunión', key='reason')
    observations = st.text_input('Ingresa observaciones', key='observations')

    if st.button('Reservar'):
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        c.execute("INSERT INTO reservas (sala_id, fecha, hora_inicio, hora_fin, nombre_reservante, email_reservante, invitados, motivo, observaciones) VALUES (?,?,?,?,?,?,?,?,?)",
                  (4, selected_date_str, selected_start_time, selected_end_time, name, email, guests, reason, observations))
        conn.commit()
        st.write('Tu reserva ha sido exitosa')
        st.write('Tu reserva es para el día:', selected_date_str)
        st.write('Desde las:', selected_start_time)
        st.write('Hasta las:', selected_end_time)

elif sala == 'Mar':
    #add code for Mar
    st.write('Estás a punto de reservar Mar')
    selected_date = st.date_input('Selecciona una fecha', today, key='date')

    list_of_availability = find_available_sala(5, str(selected_date))
    st.write("Disponible entre:")
    for start_time, end_time in list_of_availability:
        st.write(f"{start_time} - {end_time}")

    selected_start_time = st.time_input('Selecciona una hora de inicio para tu reserva', key='start_time')
    selected_end_time = st.time_input('Selecciona una hora de fin para tu reserva', key='end_time')

    name = st.text_input('Ingresa tu nombre', key='name')
    email = st.text_input('Ingresa tu email', key='email')
    guests = st.text_input('Ingresa los nombres de tus invitados', key='guests')
    reason = st.text_input('Ingresa el motivo de la reunión', key='reason')
    observations = st.text_input('Ingresa observaciones', key='observations')

    if st.button('Reservar'):
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        c.execute("INSERT INTO reservas (sala_id, fecha, hora_inicio, hora_fin, nombre_reservante, email_reservante, invitados, motivo, observaciones) VALUES (?,?,?,?,?,?,?,?,?)",
                  (5, selected_date_str, selected_start_time, selected_end_time, name, email, guests, reason, observations))
        conn.commit()
        st.write('Tu reserva ha sido exitosa')
        st.write('Tu reserva es para el día:', selected_date_str)
        st.write('Desde las:', selected_start_time)
        st.write('Hasta las:', selected_end_time)

conn.close()
