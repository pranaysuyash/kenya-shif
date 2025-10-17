"""
Output Manager - Handles file operations for local, cloud, and historical scenarios
Works on all platforms: local, Replit, Vercel, Streamlit Cloud
"""

import os
import json
import zipfile
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime


class OutputManager:
    """Manages output files for local and cloud deployment"""
    
    def __init__(self, output_base: str = "outputs"):
        self.output_base = Path(output_base)
        self.output_base.mkdir(exist_ok=True)
        self.is_cloud = os.getenv('DEPLOYMENT_ENV') in ['replit', 'vercel', 'streamlit_cloud']
        self.current_run_dir = None
        self.is_ephemeral = False
        
    def create_run_directory(self) -> Path:
        """Create timestamped directory for this run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_base / f"run_{timestamp}"
        try:
            run_dir.mkdir(parents=True, exist_ok=True)
            self.current_run_dir = run_dir
            self.is_ephemeral = False
            return run_dir
        except Exception as e:
            print(f"⚠️ Could not create persistent directory: {e}")
            print("   Using ephemeral in-memory storage")
            self.is_ephemeral = True
            return run_dir
    
    def save_dataframe(self, df: pd.DataFrame, filename: str) -> Optional[Path]:
        """Save DataFrame to CSV (local) or return BytesIO (cloud)"""
        if self.current_run_dir is None:
            self.create_run_directory()
        
        filepath = self.current_run_dir / filename
        try:
            df.to_csv(filepath, index=False)
            return filepath
        except Exception as e:
            print(f"⚠️ Could not save {filename}: {e}")
            return None
    
    def save_json(self, data: Dict, filename: str) -> Optional[Path]:
        """Save JSON data (local) or return BytesIO (cloud)"""
        if self.current_run_dir is None:
            self.create_run_directory()
        
        filepath = self.current_run_dir / filename
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return filepath
        except Exception as e:
            print(f"⚠️ Could not save {filename}: {e}")
            return None
    
    def get_all_outputs(self) -> Dict[str, str]:
        """Get dictionary of all output files in current run"""
        if self.current_run_dir is None or not self.current_run_dir.exists():
            return {}
        
        outputs = {}
        for file in self.current_run_dir.glob('*'):
            if file.is_file():
                outputs[file.name] = str(file)
        return outputs
    
    def create_download_zip(self) -> Tuple[bytes, str]:
        """Create ZIP file of all outputs for download"""
        if self.current_run_dir is None or not self.current_run_dir.exists():
            return b'', 'empty.zip'
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in self.current_run_dir.glob('*'):
                if file.is_file():
                    zip_file.write(file, arcname=file.name)
        
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shif_analysis_{timestamp}.zip"
        
        return zip_buffer.getvalue(), filename
    
    def get_historical_runs(self) -> List[Path]:
        """Get list of all previous run directories"""
        if not self.output_base.exists():
            return []
        
        runs = sorted([d for d in self.output_base.glob('run_*') if d.is_dir()],
                      key=lambda x: x.name, reverse=True)
        return runs
    
    def load_run_data(self, run_path: str) -> Dict:
        """Load all data from a historical run"""
        run_path = Path(run_path)
        if not run_path.exists():
            return {}
        
        data = {}
        try:
            for csv_file in run_path.glob('*.csv'):
                data[csv_file.stem] = pd.read_csv(csv_file)
            
            for json_file in run_path.glob('*.json'):
                with open(json_file, 'r') as f:
                    data[json_file.stem] = json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading run data: {e}")
        
        return data
    
    def get_deployment_info(self) -> Dict[str, str]:
        """Get information about current deployment"""
        return {
            'is_cloud': str(self.is_cloud),
            'is_ephemeral': str(self.is_ephemeral),
            'deployment_env': os.getenv('DEPLOYMENT_ENV', 'local'),
            'output_base': str(self.output_base),
            'current_run_dir': str(self.current_run_dir) if self.current_run_dir else 'None',
        }


class DownloadManager:
    """Handles creating downloadable files for Streamlit"""
    
    @staticmethod
    def dataframe_to_bytes(df: pd.DataFrame) -> bytes:
        """Convert DataFrame to CSV bytes"""
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue().encode()
    
    @staticmethod
    def dict_to_json_bytes(data: Dict) -> bytes:
        """Convert dictionary to JSON bytes"""
        return json.dumps(data, indent=2, default=str).encode()
    
    @staticmethod
    def create_multi_file_zip(files: Dict[str, any]) -> bytes:
        """Create ZIP containing multiple files
        
        Args:
            files: Dict with filename -> content (DataFrame, dict, str, or bytes)
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.items():
                if isinstance(content, pd.DataFrame):
                    csv_bytes = DownloadManager.dataframe_to_bytes(content)
                    zip_file.writestr(filename, csv_bytes)
                elif isinstance(content, dict):
                    json_bytes = DownloadManager.dict_to_json_bytes(content)
                    zip_file.writestr(filename, json_bytes)
                elif isinstance(content, str):
                    zip_file.writestr(filename, content)
                elif isinstance(content, bytes):
                    zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()


class HistoricalAnalysisLoader:
    """Load and display historical analysis results"""
    
    def __init__(self, output_manager: OutputManager):
        self.om = output_manager
    
    def get_historical_runs_list(self) -> List[Dict]:
        """Get formatted list of historical runs"""
        runs = self.om.get_historical_runs()
        return [
            {
                'path': str(run_path),
                'timestamp': run_path.name.replace('run_', ''),
                'files': len(list(run_path.glob('*')))
            }
            for run_path in runs
        ]
    
    def load_analysis(self, run_path: str) -> Dict:
        """Load full analysis from historical run"""
        return self.om.load_run_data(run_path)
    
    def get_summary(self, run_data: Dict) -> Dict:
        """Generate summary of loaded analysis"""
        summary = {
            'policy_services': len(run_data.get('rules_p1_18_structured', pd.DataFrame())),
            'annex_procedures': len(run_data.get('annex_surgical_tariffs_all', pd.DataFrame())),
            'ai_contradictions': len(run_data.get('ai_contradictions', pd.DataFrame())),
            'ai_gaps': len(run_data.get('ai_gaps', pd.DataFrame())),
            'files_count': len(run_data),
        }
        return summary
