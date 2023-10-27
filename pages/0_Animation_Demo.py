# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

import numpy as np

import streamlit as st
from streamlit.hello.utils import show_code


def membros() -> None:

    # Interactive Streamlit elements, like these sliders, return their value.
    # This gives you an extremely simple interaction model.
    col1, col2, col3 = st.columns(3)
    col1.image(image="cachorro.jpg")
    col1.write("Tambosi")



st.set_page_config(page_title="Membros", page_icon=":happy:")

st.sidebar.header(":happy: Membros")
st.write(
    """Aqui estão os membros da República FGV 2023"""
)

membros()
