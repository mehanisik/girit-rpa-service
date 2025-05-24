import time

def run_script(job_id_str: str, parameters: dict, input_files_metadata: list, job_log_func):
    """
    A placeholder RPA bot script.

    Args:
        job_id_str (str): The ID of the current job (as a string).
        parameters (dict): Parameters provided for this job run.
        input_files_metadata (list): A list of dictionaries, each describing an uploaded file.
                                    Example: [{'original_filename': 'invoice.pdf', 
                                              'storage_path': '/path/to/uploads/job_id/invoice.pdf', 
                                              'mimetype': 'application/pdf'}]
        job_log_func (function): A function to call for logging, e.g., 
                                 job_log_func(job_id_str_or_uuid, level, message, source="script")
    """
    source_name = __name__ 

    job_log_func(job_id_str, "SCRIPT_INFO", f"Placeholder bot script '{source_name}' started.", source=source_name)
    job_log_func(job_id_str, "SCRIPT_INFO", f"Parameters received: {parameters}", source=source_name)
    job_log_func(job_id_str, "SCRIPT_INFO", f"Input files metadata: {input_files_metadata}", source=source_name)

    if input_files_metadata:
        for file_meta in input_files_metadata:
            job_log_func(job_id_str, "SCRIPT_INFO", f"Processing file: {file_meta.get('original_filename')} at {file_meta.get('storage_path')}", source=source_name)

    else:
        job_log_func(job_id_str, "SCRIPT_INFO", "No input files provided for this job.", source=source_name)


    for i in range(3): 
        job_log_func(job_id_str, "SCRIPT_INFO", f"Working... step {i+1}/3", source=source_name)
        time.sleep(1) 

    job_log_func(job_id_str, "SCRIPT_INFO", f"Placeholder bot script '{source_name}' finished successfully.", source=source_name)
    return "Placeholder script executed successfully. See logs for details."