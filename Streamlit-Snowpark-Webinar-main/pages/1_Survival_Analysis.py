from typing import Iterable

from snowflake.snowpark.session import Session
from snowflake.snowpark.table import Table

import streamlit as st
import altair as alt
from toolz.itertoolz import pluck

from lib.filterwidget import MyFilter

MY_TABLE = "TITANIC"


def _get_active_filters() -> filter:
    return filter(lambda _: _.is_enabled, st.session_state.filters)


def _is_any_filter_enabled() -> bool:
    return any(pluck("is_enabled", st.session_state.filters))


def _get_human_filter_names(_iter: Iterable) -> Iterable:
    return pluck("human_name", _iter)


def draw_sidebar():
    """Should include dynamically generated filters"""

    with st.sidebar:
        selected_filters = st.multiselect(
            "Select which filters to enable",
            list(_get_human_filter_names(st.session_state.filters)),
            [],
        )
        for _f in st.session_state.filters:
            if _f.human_name in selected_filters:
                _f.enable()

        if _is_any_filter_enabled():
            with st.form(key="input_form"):
                for _f in _get_active_filters():
                    _f.create_widget()
                st.session_state.clicked = st.form_submit_button(label="Submit")
        else:
            st.write("Please enable a filter")


def draw_main_ui(_session: Session):
    """Contains the logic and the presentation of main section of UI"""
    active_table: Table = _session.table(MY_TABLE)
    _f: MyFilter
    for _f in _get_active_filters():
        # filter will be dynamically applied to the dataframe using the API from MyFilter
        active_table = active_table[_f(active_table)]

    st.subheader("Survival")
    by_gender = active_table.group_by(['SURVIVED']).count().to_pandas()
    c = alt.Chart(by_gender).mark_bar().encode(x='SURVIVED', y='COUNT', color='SURVIVED')
    st.altair_chart(c, use_container_width=True)
    st.write("**Snowpark generated SQL:**")
    st.write("``" + active_table.queries['queries'][0] + "``")


MyFilter.session = st.session_state['snowpark_session']
MyFilter.table_name = MY_TABLE
st.session_state.filters = (
    MyFilter(
        human_name="Gender",
        table_column="sex",
        widget_id="gender_selectbox",
        widget_type=st.selectbox,
    ),
    MyFilter(
        human_name="Age",
        table_column="AGE",
        widget_id="age_slider",
        widget_type=st.select_slider,
    ),
    MyFilter(
        human_name="Fare",
        table_column="fare",
        widget_id="fare_slider",
        widget_type=st.select_slider,
    ),
    MyFilter(
        human_name="Class",
        table_column="pclass",
        widget_id="class_selectbox",
        widget_type=st.selectbox,
    ),
    MyFilter(
        human_name="Port of Departure",
        table_column="EMBARKED",
        widget_id="port_selectbox",
        widget_type=st.selectbox,
    ),
)

draw_sidebar()
draw_main_ui(MyFilter.session)
