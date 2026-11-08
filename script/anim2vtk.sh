#!/usr/bin/bash

# animtovtkhdf.py anim* out.vtkhdf

for file in ./*; do
	if [ -n "${file: -3}" ] && [ "${file: -3}" -eq "${file: -3}" ] 2>/dev/null && [[ "${file: -4:1}" == "A" ]]; then
		anim_to_vtk_linux64_gf $file > "$file.vtk"
		echo "$file is converted"
	elif  [[ "${file: -3}" == "T01" ]] ;then
		th_to_csv_linux64_gf $file
        echo "$file is converted"
        csv="$file.csv"
	fi
done

# paraview ./$jobname"A..vtk" $csv
