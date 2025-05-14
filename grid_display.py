import streamlit as st
import pandas as pd
import base64
import io
import uuid

def display_grid(data):
    """
    Display data in a styled grid with search functionality and download option

    Args:
        data: Either a pandas DataFrame or a string that can be converted to a DataFrame
    """
    # Convert string data to DataFrame if needed
    if isinstance(data, str):
        try:
            # Try to parse as markdown table
            lines = data.strip().split('\n')
            if len(lines) > 1 and '|' in lines[0]:
                # Clean up the markdown table format
                header = lines[0].strip('|').split('|')
                header = [h.strip() for h in header]

                # Skip separator line if present
                start_idx = 1
                if len(lines) > 1 and all(c in '|-:' for c in lines[1].replace(' ', '')):
                    start_idx = 2

                rows = []
                for i in range(start_idx, len(lines)):
                    if '|' in lines[i]:
                        row = lines[i].strip('|').split('|')
                        row = [cell.strip() for cell in row]
                        rows.append(row)

                # Create DataFrame
                df = pd.DataFrame(rows, columns=header)
            else:
                # Not a markdown table, display as text
                st.markdown(data)
                return
        except Exception as e:
            st.error(f"Error parsing data: {str(e)}")
            st.markdown(data)
            return
    else:
        df = data

    # Create a container for the grid
    st.markdown('<div class="data-grid-container">', unsafe_allow_html=True)

    # Header with title and search
    st.markdown('<div class="data-grid-header">', unsafe_allow_html=True)
    st.markdown('<div class="data-grid-title">Results</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Add search functionality
    st.markdown('<div class="data-grid-search">', unsafe_allow_html=True)
    search_key = f"grid_search_{uuid.uuid4()}"
    search_term = st.text_input("Search in results:", key=search_key)
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter the dataframe if search term is provided
    if search_term:
        # Convert all columns to string for searching
        df_str = df.astype(str)

        # Check each column for the search term
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask = mask | df_str[col].str.contains(search_term, case=False, na=False)

        filtered_df = df[mask]
    else:
        filtered_df = df

    # Display the data
    st.markdown('<div class="data-grid-content">', unsafe_allow_html=True)

    # Check if we have data to display
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No matching results found.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Add download button in footer
    st.markdown('<div class="data-grid-footer">', unsafe_allow_html=True)

    # Create a download button for the data
    csv = convert_df_to_csv(df)
    download_key = f"download_csv_{uuid.uuid4()}"
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="quran_results.csv",
        mime="text/csv",
        key=download_key,
        help="Download the full results as a CSV file"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Close the container
    st.markdown('</div>', unsafe_allow_html=True)


def convert_df_to_csv(df):
    """
    Convert DataFrame to CSV for download
    """
    # Create a string buffer
    buffer = io.StringIO()

    # Write the DataFrame to the buffer
    df.to_csv(buffer, index=False)

    # Get the string value and return
    return buffer.getvalue()

