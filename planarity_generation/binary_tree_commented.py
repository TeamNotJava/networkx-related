# Stuff from the huge paper
# 
# # Sampler for K underscore =
# if Bern(R_b_as/K underscore) then R_b_as else R_w_as


# Sampler for R_b_as =
# switch Bern()
# case A:
# sampler for (R_w * Z_L * Z_U)
# case B:
# sampler for (Z_U * Z_L * R_W)
# default
# sampler for (Z_L * R_w * R_w)


# Sampler for R_w_as = 
# switch Bern()
# case A:
# sampler for (R_^_b * Z_U)
# case B:
# sampler for (Z_U * R_^_b)
# default:
# R_b * R_b

# Sampler for R_^_b = 
# switch Bern()
# case A:
# sampler for (R_^_w * Z_L Z_U * Z_U)
# case B:
# sampler for (Z_U * Z_U Z_L R_w)
# default:
# sampler for (R_^_w * Z_L R_^_w)

# Sampler for R_^_w = 
# switch Bern()
# case A:
# Z_U
# case B:
# sampler for (R_b * Z_U)
# case D:
# sampler for Z_U * R_b
# default:
# sampler for (R_b * R_b)

# Sampler for R_b = 
# (if Bern(Z_U) then Z_U else R_w ) * Z_L * (if Bern(Z_U) then Z_U else R_w)

# Sampler for R_w =
# # (if Bern(Z_U) then Z_U else R_b ) * (if Bern(Z_U) then Z_U else R_b)