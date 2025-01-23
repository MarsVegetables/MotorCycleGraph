import argparse
import pyvista as pv
import numpy as np
import Alg

def unique_edges(edges):
    return set(tuple(sorted(edge)) for edge in edges)

def read_obj_file(file_path):
	vertices = []
	faces = []
	with open(file_path, 'r') as obj_file:
		for line in obj_file:
			tokens = line.strip().split()
			if tokens:
				if tokens[0] == 'v':
					vertex = [float(token) for token in tokens[1:]]
					vertices.append(vertex)
				elif tokens[0] == 'f':
					vertex_indices = [int(token.split('/')[0]) for token in tokens[1:]]
					faces.append(vertex_indices)
	return np.array(vertices), np.array(faces)


# def extract_edges_from_faces(faces):
# 	edges = []
# 	for quad in faces:
# 		v0, v1, v2, v3 = quad[0] - 1, quad[1] - 1, quad[2] - 1, quad[3] - 1
# 		edges.extend([(v0, v1), (v1, v2), (v2, v3), (v3, v0)])
# 	return np.array(edges)

def extract_edges_from_faces(faces):
	edges = []
	for quad in faces:
		v0, v1, v2, v3 = quad[0], quad[1], quad[2], quad[3]
		edges.extend([(v0, v1), (v1, v2), (v2, v3), (v3, v0)])
	return np.array(edges)

def count_vertex_faces(faces):
	vertex_face_count = {}
	for face in faces:
		for vertex_id in face:
			if vertex_id in vertex_face_count:
				vertex_face_count[vertex_id] += 1
			else:
				vertex_face_count[vertex_id] = 1
	return vertex_face_count


def find_extraordinary_vertices(vertex_face_count):
	vertices_with_more_than_4_faces = [vertex_id for vertex_id, count in vertex_face_count.items() if count > 4]
	vertices_with_less_than_4_faces = [vertex_id for vertex_id, count in vertex_face_count.items() if count < 4]
	extraordinary_vertices = vertices_with_more_than_4_faces + vertices_with_less_than_4_faces
	return list(set(extraordinary_vertices))


def main(file_path):
	# vertices, faces = read_obj_file(file_path)
	# edges = extract_edges_from_faces(faces)

	mesh = pv.read(file_path)
	mesh.plot(show_edges=True)

	faces = mesh.faces.reshape(-1, 5)[:, 1:]  # n_faces x 4
	vertices = mesh.points
	edges = extract_edges_from_faces(faces)
	edges = list(unique_edges(edges))
	vertex_face_count = count_vertex_faces(faces)
	extraordinary_vertices_list = find_extraordinary_vertices(vertex_face_count)

	# # Check edges for a specific face
	# face_idx = 0  # Change this to check different faces
	# face = faces[face_idx]
	# face_edges = np.vstack((face, np.roll(face, -1))).T
	# print(f"Face edges:\n{face_edges}")
	# print("Which of these appear in edges array:")
	# for edge in face_edges:
	# 	exists = np.any(np.all(edges == edge, axis=1) | np.all(edges == edge[::-1], axis=1))
	# 	print(f"{edge}: {exists}")
	#
	# # Get face edges accounting for both orientations
	# def check_face_edges(face, edge_list):
	# 	face_edges = np.vstack((face, np.roll(face, -1))).T
	# 	for e in face_edges:
	# 		# Check both orientations
	# 		forward = np.any(np.all(edge_list == e, axis=1))
	# 		reverse = np.any(np.all(edge_list == e[::-1], axis=1))
	# 		print(f"{e}: forward={forward}, reverse={reverse}")
	#
	# check_face_edges(faces[face_idx], edges)

	print(f"vertex counts: {len(vertex_face_count)}")
	print(f"singular vertex counts: {len(extraordinary_vertices_list)}")
	print(f"ratio: {len(extraordinary_vertices_list) / len(vertex_face_count)}")

	extraordinary_vertices_array = np.array(extraordinary_vertices_list)
	extraordinary_coords = vertices[extraordinary_vertices_array - 1]

	boundary_vertex_ids_empty = []
	boundary_edges_empty = []

	motorcycle_graph = Alg.MotorcycleGraph(mesh, vertices, faces, edges, extraordinary_vertices_array,
	                                       boundary_vertex_ids_empty, boundary_edges_empty)

	motorcycle_graph.constructMotorcycleGraph()


# Uncomment the following lines if needed
# motorcycle_graph.write_extraOrdinary_vertices("ellipse_smooth")
# motorcycle_graph.save_motorcycle_edges_info("ellipse_smooth.obj")
# motorcycle_graph.write_submeshes_info("6_rem_p0_0_quadrangulation_smooth.obj")
# motorcycle_graph.write_submeshes_as_new_meshes("6_rem_p0_0_quadrangulation_smooth.obj")

# main(".\\Models\\6_rem_p0_0_quadrangulation_smooth.obj")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Process an OBJ file to construct a motorcycle graph.")
	parser.add_argument('file_path', type=str, nargs='?', help="Path to the OBJ file")
	args = parser.parse_args()

	if not args.file_path:
		print("Error: No file path provided.")
		print("Usage: python main.py <path_to_obj_file>")
	else:
		main(args.file_path)
